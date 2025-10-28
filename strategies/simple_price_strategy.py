import logging
from typing import Any, Dict, List, Optional

from models import SignalType
from models.events import MarketEvent
from strategies import BaseStrategy
from event_bus import EventBus


logger = logging.getLogger(__name__)


class SimplePriceStrategy(BaseStrategy):
    """
    Estrategia simple que genera señales de compra y venta basadas en el precio.
    """

    def __init__(self, name: str, symbols: List[str], event_bus: EventBus, parameters: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(name, symbols, event_bus, parameters)
        logger.info(f"Inicializando SimplePriceStrategy: {self.name} para símbolos: {self.symbols}")

    def calculate_signal(self, market_event: MarketEvent) -> SignalType | None:
        """Calcula la señal basada en la relación open/close."""

        if not market_event or not market_event.data:
            self.logger.warning(f"Estrategia '{self.name}': Datos de mercado no disponibles para el símbolo {market_event.symbol}")
            return None
        
        # Extraer precios de apertura y cierre del diccionario 'data'
        open_price = market_event.data.get("open")
        close_price = market_event.data.get("close")

        # Verificar que tenemos ambos precios
        if open_price is None or close_price is None:
            self.logger.warning(f"Estrategia '{self.name}': Precios de apertura o cierre no disponibles para el símbolo {market_event.symbol}")
            return None
        
        self.logger.debug(f"Estrategia '{self.name}': Símbolo {market_event.symbol} - Open: {open_price}, Close: {close_price}")

        # Lógica simple de señal
        if close_price > open_price:
            self.logger.info(f"Generando señal LONG para {market_event.symbol} (Close > Open)")
            return SignalType.LONG
        elif close_price < open_price:
            self.logger.info(f"Generando señal EXIT para {market_event.symbol} (Close < Open)")
            return SignalType.EXIT
        else:
            return None
