from abc import ABC, abstractmethod

from models import SignalEvent
from portfolio import IPortfolio
from data import IDataHandler


class IOrderSizer(ABC):
    """
    Interfaz para los componentes de dimensionamiento de órdenes.
    """

    @abstractmethod
    def calculate_quantity(self, signal: SignalEvent, portfolio: IPortfolio, data_handler: IDataHandler) -> float:
        """Calcula la cantidad (positiva) de la orden a ejecutar."""
        raise NotImplementedError