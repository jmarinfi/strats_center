from abc import ABC, abstractmethod
from queue import Queue
from typing import Optional

from models.events import MarketEvent


class IDataHandler(ABC):
    """
    Clase abstracta para manejadores de datos de mercado, tanto históricos como en vivo.
    """

    events_queue: Queue[MarketEvent]

    @property
    @abstractmethod
    def continue_backtest(self) -> bool:
        """Indica si el backtesting debe continuar."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")

    @abstractmethod
    def get_latest_bars(self, N: int = 1):
        """Retorna las últimas N barras."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")
    
    @abstractmethod
    def update_bars(self):
        """Avanza el feed de datos en un paso y coloca un MarketEvent en la cola de eventos."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")
    