from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Set

import pandas as pd

from event_bus import BaseEventHandler, EventBus
from models import SignalEvent, EventType, Event, MarketEvent, SignalType


class BaseStrategy(BaseEventHandler, ABC):
    """
    Clase base abstracta para estrategias de trading.
    """

    def __init__(self, name: str, symbols: List[str], event_bus: EventBus, parameters: Optional[Dict[str, Any]] = None) -> None:
        """Inicializa la estrategia con un nombre, símbolos y parámetros opcionales."""
        super().__init__(name)
        self.name = name
        self.symbols = set(symbols)
        self.parameters = parameters or {}
        self.event_bus = event_bus

        # Estado interno
        self._market_data: Dict[str, pd.DataFrame] = {}
        self._last_signals: Dict[str, SignalEvent] = {}
        self._is_active = True

        # Configuración de logging
        self.logger = logging.getLogger(f"{__name__}.{self.name}")

        self.logger.info(f"Estrategia '{self.name}' inicializada con símbolos: {self.symbols}")

    @property
    def supported_events(self) -> Set[EventType]:
        """Eventos que maneja esta estrategia."""
        return {EventType.MARKET}
    
    def handle(self, event: Event) -> None:
        """Handler principal de eventos. Distribuye según el tipo de evento."""
        if not self._is_active:
            return
        
        if isinstance(event, MarketEvent):
            self._handle_market_event(event)
        else:
            self.logger.warning(f"Estrategia '{self.name}' recibió evento no soportado: {event.type}")
    
    def _handle_market_event(self, event: MarketEvent) -> None:
        """Procesa un evento de mercado."""
        # Filtrar por símbolos de interés
        if event.symbol not in self.symbols:
            return
        
        try:
            # Actualizar datos internos
            self._update_market_data(event)

            # Ejecutar lógica de la estrategia
            signal = self.calculate_signal(event)

            # Generar señal si es necesaria
            if signal is not None:
                self._emit_signal(signal, event)

        except Exception as e:
            self.logger.error(f"Error procesando MarketEvent para símbolo {event.symbol}: {e}")

    def _update_market_data(self, event: MarketEvent) -> None:
        """Actualiza el cache interno de datos de mercado."""
        symbol = event.symbol

        # Inicializar DataFrame si no existe
        if symbol not in self._market_data:
            self._market_data[symbol] = pd.DataFrame()

        # Convertir datos del evento a fila de DataFrame
        if event.data:
            row_data = {
                'timestamp': event.timestamp,
                **event.data
            }

            # Crear nueva fila y concatenar
            new_row = pd.DataFrame([row_data])
            new_row.set_index('timestamp', inplace=True)

            self._market_data[symbol] = pd.concat([
                self._market_data[symbol],
                new_row
            ])

            # Mantener sólo los últimos N registros para eficiencia
            max_history = self.parameters.get('max_history', 1000)
            if len(self._market_data[symbol]) > max_history:
                self._market_data[symbol] = self._market_data[symbol].tail(max_history)

    def _emit_signal(self, signal_type: SignalType, market_event: MarketEvent) -> None:
        """Emite una señal de trading."""
        signal = SignalEvent(
            symbol=market_event.symbol,
            timestamp=market_event.timestamp,
            signal_type=signal_type
        )

        # Guardar referencia a la última señal
        self._last_signals[market_event.symbol] = signal

        # Emitir al Event Bus
        self.event_bus.publish(signal)
        self.logger.info(f"Estrategia '{self.name}' con símbolo {market_event.symbol} emitió señal: {signal}")

    @abstractmethod
    def calculate_signal(self, market_event: MarketEvent) -> Optional[SignalType]:
        """Lógica principal de la estrategia. Debe ser implementada por subclases."""
        pass

    def get_market_data(self, symbol: str, periods: Optional[int] = None) -> pd.DataFrame:
        """Obtiene los datos de mercado almacenados para un símbolo dado."""
        if symbol not in self._market_data:
            return pd.DataFrame()
        
        data = self._market_data[symbol]

        if periods is not None and len(data) > periods:
            return data.tail(periods)
        
        return data.copy()
    
    def get_last_signal(self, symbol: str) -> Optional[SignalEvent]:
        """Obtiene la última señal generada para un símbolo dado."""
        return self._last_signals.get(symbol)
    
    def reset(self) -> None:
        """Reinicia el estado interno de la estrategia."""
        self._market_data.clear()
        self._last_signals.clear()
        self.logger.info(f"Estrategia '{self.name}' ha sido reiniciada.")

    def activate(self) -> None:
        """Activa la estrategia para que procese eventos."""
        self._is_active = True
        self.logger.info(f"Estrategia '{self.name}' activada.")

    def deactivate(self) -> None:
        """Desactiva la estrategia para que ignore eventos."""
        self._is_active = False
        self.logger.info(f"Estrategia '{self.name}' desactivada.")

    @property
    def is_active(self) -> bool:
        """Indica si la estrategia está activa."""
        return self._is_active
    
    def get_info(self) -> Dict[str, Any]:
        """Devuelve información básica sobre la estrategia."""
        return {
            'name': self.name,
            'symbols': list(self.symbols),
            'parameters': self.parameters,
            'is_active': self._is_active,
            'data_points': {sym: len(df) for sym, df in self._market_data.items()},
            'last_signals': {sym: sig.signal_type.name for sym, sig in self._last_signals.items()}
        }
    