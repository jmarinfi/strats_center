import logging
from typing import Optional

from event_bus import EventBus
from models import Event, SignalEvent, OrderEvent, OrderType, SignalType, OrderDirection
from portfolio import IPortfolio
from data import IDataHandler
from sizing import IOrderSizer
from order_manager import IOrderManager


logger = logging.getLogger(__name__)


class SimpleOrderManager(IOrderManager):
    """
    Implementación simple de IOrderManager.
    """

    def __init__(self, event_bus: EventBus, portfolio: IPortfolio, data_handler: IDataHandler, sizer: IOrderSizer) -> None:
        super().__init__(name="SimpleOrderManager")
        self.event_bus = event_bus
        self.portfolio = portfolio
        self.data_handler = data_handler
        self.sizer = sizer

        logger.info(f"SimpleOrderManager inicializado con sizer: {type(self.sizer).__name__}")

    def handle(self, event: Event) -> None:
        """Maneja los eventos de señal."""
        if not isinstance(event, SignalEvent):
            self.logger.warning(f"Evento no soportado recibido en SimpleOrderManager: {event}")
            return
        
        logger.debug(f"OrderManager: Procesando SignalEvent para {event.symbol} de tipo {event.signal_type}")

        # Determinar la dirección
        direction = self._calculate_direction(event.signal_type, event.symbol)
        if direction is None:
            logger.debug(f"OrderManager: Señal {event.signal_type} para {event.symbol} no requiere orden. Ignorando.")
            return
        
        # Calcular la cantidad usando el sizer
        quantity = self.sizer.calculate_quantity(event, self.portfolio, self.data_handler)
        if quantity <= 1e-8:
            logger.debug(f"OrderManager: Cantidad calculada es cero para {event.symbol}. No se crea orden.")
            return
        
        # Crear y publicar la orden
        order = OrderEvent(
            symbol=event.symbol,
            timestamp=event.timestamp,
            order_type=OrderType.MARKET,
            direction=direction,
            quantity=quantity,
        )

        logger.info(
            f"OrderManager publicando OrderEvent: {order.direction} {order.quantity} de {order.symbol} "
            f"a las {order.timestamp}"
        )
        self.event_bus.publish(order)

    def _calculate_direction(self, signal_type: SignalType, symbol: str) -> Optional[OrderDirection]:
        """Calcula la dirección de la orden basada en el tipo de señal y la posición actual."""
        current_position = self.portfolio.get_position_size(symbol)
        pos_is_long = current_position > 1e-8
        pos_is_short = current_position < -1e-8
        pos_is_flat = not pos_is_long and not pos_is_short

        if signal_type == SignalType.LONG:
            if pos_is_long:
                logger.debug(f"OrderManager: Ya en posición LONG para {symbol}. No se crea orden.")
                return None
            if pos_is_short:
                logger.warning(f"OrderManager: Señal LONG para {symbol} pero ya en posición SHORT. No se maneja reversión.")
                return None
            return OrderDirection.BUY
        
        elif signal_type == SignalType.SHORT:
            if pos_is_short:
                logger.debug(f"OrderManager: Ya en posición SHORT para {symbol}. No se crea orden.")
                return None
            if pos_is_long:
                logger.warning(f"OrderManager: Señal SHORT para {symbol} pero ya en posición LONG. No se maneja reversión.")
                return None
            return OrderDirection.SELL
        
        elif signal_type == SignalType.EXIT:
            if pos_is_long:
                return OrderDirection.SELL
            if pos_is_short:
                return OrderDirection.BUY
            
            logger.debug(f"OrderManager: Señal EXIT para {symbol} pero ya en posición FLAT. No se crea orden.")
            return None
        
        return None
