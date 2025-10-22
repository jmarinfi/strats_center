from abc import ABC, abstractmethod


class IDataHandler(ABC):
    """
    Clase abstracta para manejadores de datos de mercado, tanto históricos como en vivo.
    """

    @abstractmethod
    def get_latest_bars(self, N: int = 1):
        """Retorna las últimas N barras."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")
    
    @abstractmethod
    def update_bars(self):
        """Avanza el feed de datos en un paso y coloca un MarketEvent en la cola de eventos."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")