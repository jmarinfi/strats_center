from abc import ABC, abstractmethod
from typing import Set

from event_bus import BaseEventHandler
from models import EventType, Event


class IBroker(BaseEventHandler, ABC):
    """
    Interfaz abstracta para todos los brokers, simulados o en vivo.
    """

    @property
    def supported_events(self) -> Set[EventType]:
        """Define el contrato para todos los brokers sobre los tipos de eventos que pueden manejar."""
        return {EventType.ORDER}
    