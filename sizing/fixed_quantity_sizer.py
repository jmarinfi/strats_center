import logging

from data import IDataHandler
from models import SignalEvent, SignalType
from portfolio import IPortfolio
from sizing import IOrderSizer


logger = logging.getLogger(__name__)


class FixedQuantitySizer(IOrderSizer):
    """
    Implementación simple de IOrderSizer.
    """

    def __init__(self, default_quantity: float = 0.1) -> None:
        if default_quantity <= 0:
            raise ValueError("La cantidad fija debe ser un valor positivo.")
        self.default_quantity = default_quantity
        logger.info(f"FixedQuantitySizer inicializado con cantidad fija: {self.default_quantity}")

    def calculate_quantity(self, signal: SignalEvent, portfolio: IPortfolio, data_handler: IDataHandler) -> float:
        """Calcula la cantidad fija para la orden."""
        symbol = signal.symbol

        if signal.signal_type == SignalType.EXIT:
            # Para un EXIT, la cantidad es la posición actual absoluta.
            current_position = portfolio.get_position_size(symbol)
            quantity = abs(current_position)

            if quantity > 1e-8: # Evitar órdenes de polvo
                logger.debug(
                    f"Sizer: Señal EXIT para {symbol}. "
                    f"Posición actual: {current_position}, cantidad a cerrar: {quantity}"
                )
                return quantity
            else:
                logger.debug(f"Sizer: Señal EXIT para {symbol} pero no hay posición ({current_position}). Cantidad: 0.0")
                return 0.0
            
        elif signal.signal_type == SignalType.LONG or signal.signal_type == SignalType.SHORT:
            logger.debug(
                f"Sizer: Señal {signal.signal_type} para {symbol}. "
                f"Cantidad fija asignada: {self.default_quantity}"
            )
            return self.default_quantity
        
        else:
            logger.warning(f"Sizer: Tipo de señal desconocido {signal.signal_type} para {symbol}. Cantidad: 0.0")
            return 0.0
        