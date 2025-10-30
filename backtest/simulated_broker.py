import logging

from broker import IBroker
from event_bus import EventBus
from data import IDataHandler
from models import CommissionConfig, OrderEvent, Event, OrderType, FillEvent, CommissionType


logger = logging.getLogger(__name__)


class SimulatedBroker(IBroker):
    """
    Implementación de IBroker que simula la ejecución de órdenes en un entorno de backtesting.
    """

    def __init__(self, event_bus: EventBus, commission_config: CommissionConfig, data_handler: IDataHandler):
        super().__init__("SimulatedBroker")

        self.event_bus = event_bus
        self.commission_config = commission_config
        self.data_handler = data_handler

        self.logger.info(
            f"SimulatedBroker inicializado con comisión: {commission_config.rate*100:.2f}% ({commission_config.type.value})"
        )

    def handle(self, event: Event) -> None:
        """Maneja los eventos entrantes."""
        if isinstance(event, OrderEvent):
            self._execute_order(event)
        else:
            self.logger.warning(f"SimulatedBroker recibió un evento no soportado: {event}")

    def _execute_order(self, event: OrderEvent) -> None:
        """
        Simula la ejecución de una orden. Asumimos que todas la órdenes MARKET se ejecutan
        inmediatamente al precio de cierre de la vela actual.
        """
        if event.order_type != OrderType.MARKET:
            self.logger.warning(f"SimulatedBroker solo soporta órdenes MARKET. Orden ignorada: {event}")
            return
        
        # Obtenemos el precio de ejecución desde el DataHandler
        try:
            latest_bars = self.data_handler.get_latest_bars(1)
            if not latest_bars:
                self.logger.warning(f"No hay datos de mercado para {event.symbol}. Orden no ejecutada.")
                return
            
            # Asumimos la ejecución al precio de cierre de la vela actual
            fill_price = self.data_handler.get_latest_price(event.symbol)

            if fill_price is None:
                self.logger.warning(f"No se pudo obtener el precio de cierre para {event.symbol}. Orden no ejecutada.")
                return
            
        except Exception as e:
            self.logger.error(f"Error al obtener el precio de ejecución para {event.symbol}: {e}")
            return
        
        fill_cost = fill_price * event.quantity
        commission = self._calculate_commission(fill_cost)

        fill_event = FillEvent(
            timestamp=event.timestamp,
            symbol=event.symbol,
            exchange="SIMULATED",
            quantity=event.quantity,
            direction=event.direction,
            fill_cost=fill_cost,
            commission=commission
        )

        self.logger.info(
            f"Orden ejecutada: {event.quantity} {event.symbol} a {fill_price:.2f} "
            f"con comisión {commission:.2f}"
        )

        # Publicamos el FillEvent en el EventBus
        self.event_bus.publish(fill_event)

    def _calculate_commission(self, fill_cost: float) -> float:
        """Calcula la comisión basada en la configuración."""
        if self.commission_config.type == CommissionType.PERCENTAGE:
            return fill_cost * self.commission_config.rate
        elif self.commission_config.type == CommissionType.FIXED:
            return self.commission_config.rate
        return 0.0
