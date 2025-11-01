from collections import defaultdict
import logging
from typing import Dict, Set

from models.events import Event
from portfolio import IPortfolio
from event_bus import EventBus
from data import IDataHandler
from models import EventType, FillEvent, OrderDirection


logger = logging.getLogger(__name__)


class SimplePortfolio(IPortfolio):
    """
    Implementación simple de IPortfolio para backtesting.
    """

    def __init__(self, event_bus: EventBus, data_handler: IDataHandler, initial_capital: float = 10000.0) -> None:
        super().__init__(name="SimplePortfolio")
        self.event_bus = event_bus
        self.data_handler = data_handler
        self.initial_capital = initial_capital
        self.current_cash = initial_capital

        self.positions: Dict[str, float] = defaultdict(float)

        logger.info(f"SimplePortfolio inicializado con capital inicial: {self.initial_capital}")

    @property
    def supported_events(self) -> Set[EventType]:
        """Define los tipos de eventos que la cartera puede manejar."""
        return {EventType.FILL}
    
    def handle(self, event: Event) -> None:
        """Maneja los eventos de tipo FILL para actualizar la cartera."""
        if isinstance(event, FillEvent):
            self._update_on_fill(event)
        else:
            self.logger.warning(f"Evento no soportado recibido en SimplePortfolio: {event}")

    def _update_on_fill(self, event: FillEvent) -> None:
        """Actualiza la cartera en función de un FillEvent."""
        symbol = event.symbol
        quantity = event.quantity
        direction = event.direction
        fill_cost = event.fill_cost
        commission = event.commission

        # Actualizar la cantidad de la posición
        if direction == OrderDirection.BUY:
            self.positions[symbol] += quantity
        elif direction == OrderDirection.SELL:
            self.positions[symbol] -= quantity

        # Redondear para evitar problemas de precisión flotante
        self.positions[symbol] = round(self.positions[symbol], 8)

        # Actualizar el efectivo disponible
        if direction == OrderDirection.BUY:
            # En una compra, el costo y la comisión se restan del efectivo
            self.current_cash -= (fill_cost + commission)
        elif direction == OrderDirection.SELL:
            # En una venta, el costo se suma y la comisión se resta del efectivo
            self.current_cash += (fill_cost - commission)
        
        logger.info(
            f"Actualización de carter ({event.direction.value}): "
            f"Símbolo: {symbol}, Cantidad: {quantity}, Costo: {fill_cost}, Comisión: {commission}. "
        )

    def get_position_size(self, symbol: str) -> float:
        """Retorna la cantidad de la posición actual para un símbolo dado."""
        return self.positions.get(symbol, 0.0)
    
    def get_current_cash(self) -> float:
        """Retorna el efectivo actual disponible en la cartera."""
        return self.current_cash
    
    # --- Métodos Específicos para Backtesting ---

    def print_final_stats(self) -> None:
        """Imprime las estadísticas finales de la cartera al finalizar el backtesting."""
        self.logger.info("=" * 60)
        self.logger.info("FIN DEL BACKTEST - RESUMEN DEL PORTAFOLIO")
        self.logger.info(f"Capital Inicial: {self.initial_capital:.2f} USD")

        total_portfolio_value = self.current_cash
        holdings_market_value = 0.0

        if not self.positions:
            self.logger.info("No se mantuvieron posiciones.")

        # Calcular el valor de mercado de las posiciones abiertas
        for symbol, quantity in self.positions.items():
            # Comprobar si hay una posición neta (evitando polvo numérico)
            if abs(quantity) > 1e-8:
                last_price = self.data_handler.get_latest_price(symbol)
                if last_price is None:
                    last_price = 0.0
                    self.logger.warning(f"No se encontró el precio para el símbolo {symbol}. Usando 0.0 como precio.")

                market_value = quantity * last_price
                holdings_market_value += market_value
                self.logger.info(
                    f"Posición en {symbol}: Cantidad: {quantity:.6f}, Precio Último: {last_price:.2f}, "
                    f"Valor de Mercado: {market_value:.2f} USD"
                )

        total_portfolio_value += holdings_market_value
        pnl_total = total_portfolio_value - self.initial_capital
        pnl_pct = (pnl_total / self.initial_capital) * 100.0

        self.logger.info("-" * 60)
        self.logger.info(f"Efectivo Final: {self.current_cash:.2f} USD")
        self.logger.info(f"Valor de Mercado de Posiciones: {holdings_market_value:.2f} USD")
        self.logger.info(f"Valor Total del Portafolio: {total_portfolio_value:.2f} USD")
        self.logger.info("-" * 60)
        self.logger.info(f"Resultado (PnL) Total: {pnl_total:.2f} USD ({pnl_pct:.2f}%)")
        self.logger.info("=" * 60)
        