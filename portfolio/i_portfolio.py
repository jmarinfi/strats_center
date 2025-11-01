from abc import ABC, abstractmethod
from typing import Set

from event_bus import BaseEventHandler
from models import EventType


class IPortfolio(BaseEventHandler, ABC):
    """
    Interfaz para la gestión de carteras de trading.
    """
    
    @property
    def supported_events(self) -> Set[EventType]:
        """Define los tipos de eventos que la cartera puede manejar."""
        return {EventType.FILL}
    
    @abstractmethod
    def get_position_size(self, symbol: str) -> float:
        """Retorna la cantidad de la posición actual para un símbolo dado."""
        raise NotImplementedError
    
    @abstractmethod
    def get_current_cash(self) -> float:
        """Retorna el efectivo actual disponible en la cartera."""
        raise NotImplementedError
    
    @abstractmethod
    def print_final_stats(self) -> None:
        """Imprime las estadísticas finales de la cartera."""
        raise NotImplementedError