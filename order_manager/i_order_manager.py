from abc import ABC
from typing import Set

from event_bus import BaseEventHandler
from models import EventType


class IOrderManager(BaseEventHandler, ABC):
    """
    Interfaz para la gestión de órdenes de trading.
    """
    
    @property
    def supported_events(self) -> Set[EventType]:
        """Define los tipos de eventos que el gestor de órdenes puede manejar."""
        return {EventType.SIGNAL}