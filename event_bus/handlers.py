from abc import ABC, abstractmethod
from collections import defaultdict
import logging
from typing import Callable, Dict, List, Optional, Set

from models import Event, EventType
from event_bus import HandlerRegistrationError, HandlerNotFoundError


logger = logging.getLogger(__name__)


class IEventHandler(ABC):
    """Interfaz para los manejadores de eventos del Event Bus."""

    @abstractmethod
    def handle(self, event: Event) -> None:
        """
        Maneja un evento específico.
        """
        raise NotImplementedError("El método handle debe ser implementado por la subclase.")
    
    @property
    @abstractmethod
    def supported_events(self) -> Set[EventType]:
        """
        Retorna un conjunto de tipos de eventos que este manejador puede procesar.
        """
        raise NotImplementedError("El método supported_events debe ser implementado por la subclase.")
    
    @property
    def handler_name(self) -> str:
        """
        Retorna el nombre del manejador.
        """
        return self.__class__.__name__
    

class EventHandlerRegistry:
    """
    Registro para manejar la asociación entre tipos de eventos y sus manejadores.
    """

    def __init__(self):
        self._handlers: Dict[EventType, List[IEventHandler]] = defaultdict(list)
        self._handler_events: Dict[IEventHandler, Set[EventType]] = {}

        logger.info("Registro de manejadores de eventos inicializado.")

    def register_handler(self, handler: IEventHandler) -> None:
        """
        Registra un manejador para sus tipos de eventos soportados.
        """
        if not isinstance(handler, IEventHandler):
            raise HandlerRegistrationError(
                event_type="unknown",
                handler_name=str(handler),
                reason="El manejador debe implementar la interfaz IEventHandler."
            )
        
        try:
            supported_events = handler.supported_events

            if not supported_events:
                raise HandlerRegistrationError(
                    event_type="none",
                    handler_name=handler.handler_name,
                    reason="El manejador no soporta ningún tipo de evento."
                )
            
            # Registrar el manejador para cada tipo de evento soportado
            for event_type in supported_events:
                if handler not in self._handlers[event_type]:
                    self._handlers[event_type].append(handler)
                    logger.debug(f"Manejador '{handler.handler_name}' registrado para el evento '{event_type.name}'.")

            # Mantener mapeo inverso
            self._handler_events[handler] = supported_events.copy()

            logger.info(f"Manejador '{handler.handler_name}' registrado exitosamente para eventos: {[et.name for et in supported_events]}.")

        except Exception as e:
            raise HandlerRegistrationError(
                event_type="unknown",
                handler_name=handler.handler_name,
                reason=f"Error al registrar el manejador: {str(e)}"
            )
        
    def unregister_handler(self, handler: IEventHandler) -> None:
        """
        Desregistra un manejador de todos sus tipos de eventos.
        """
        if handler not in self._handler_events:
            logger.warning(f"Intento de desregistrar un manejador no registrado: '{handler.handler_name}'.")
            return
        
        # Obtener eventos que maneja este handler
        supported_events = self._handler_events[handler]

        # Remover de cada lista de manejadores
        for event_type in supported_events:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                logger.debug(f"Manejador '{handler.handler_name}' desregistrado del evento '{event_type.name}'.")

        # Remover del mapeo inverso
        del self._handler_events[handler]

        logger.info(f"Manejador '{handler.handler_name}' desregistrado exitosamente.")

    def get_handlers(self, event_type: EventType) -> List[IEventHandler]:
        """
        Retorna la lista de manejadores registrados para un tipo de evento específico.
        """
        handlers = self._handlers.get(event_type, [])

        if not handlers:
            raise HandlerNotFoundError(event_type.value)
        
        return handlers.copy()
    
    def has_handlers(self, event_type: EventType) -> bool:
        """
        Verifica si hay manejadores registrados para un tipo de evento específico.
        """
        return len(self._handlers.get(event_type, [])) > 0
    
    def get_all_registered_events(self) -> Set[EventType]:
        """
        Retorna un conjunto de todos los tipos de eventos que tienen manejadores registrados.
        """
        return {event_type for event_type, handlers in self._handlers.items() if handlers}
    
    def get_handler_count(self, event_type: EventType) -> int:
        """
        Retorna el número de manejadores registrados para un tipo de evento específico.
        """
        return len(self._handlers.get(event_type, []))
    
    def clear(self) -> None:
        """
        Limpia todos los manejadores registrados.
        """
        self._handlers.clear()
        self._handler_events.clear()
        logger.info("Todos los manejadores de eventos han sido limpiados del registro.")

    def __str__(self) -> str:
        """Representación string del registro de manejadores."""
        lines = ["EventHandlerRegistry:"]

        for event_type, handlers in self._handlers.items():
            if handlers:
                handler_names = [handler.handler_name for handler in handlers]
                lines.append(f"  {event_type.name}: {handler_names}")

        return "\n".join(lines)
    

class BaseEventHandler(IEventHandler):
    """
    Implementación base de un manejador de eventos.
    """

    def __init__(self, name: Optional[str] = None):
        self._name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"{__name__}.{self._name}")

    @property
    def handler_name(self) -> str:
        return self._name
    
    def handle(self, event: Event) -> None:
        """
        Maneja un evento específico. Debe ser sobrescrito por subclases.
        """
        self.logger.debug(f"Evento recibido: {event.type.name}")

    @property
    @abstractmethod
    def supported_events(self) -> Set[EventType]:
        """
        Las subclases deben definir los tipos de eventos que soportan.
        """
        raise NotImplementedError("El método supported_events debe ser implementado por la subclase.")
    

# Funciones helper para crear handlers simples basados en funciones
def create_function_handler(
        event_types: Set[EventType],
        handler_func: Callable[[Event], None],
        name: Optional[str] = None
) -> IEventHandler:
    """
    Crea un manejador de eventos basado en una función simple.
    """

    class FunctionHandler(BaseEventHandler):
        def __init__(self):
            super().__init__(name or handler_func.__name__)
            self._handler_func = handler_func
            self._supported_events = event_types

        def handle(self, event: Event) -> None:
            self._handler_func(event)

        @property
        def supported_events(self) -> Set[EventType]:
            return self._supported_events
        
    return FunctionHandler()
