from collections import deque
import logging
from typing import List

from event_bus import EventHandlerRegistry, HandlerNotFoundError
from models import Event


logger = logging.getLogger(__name__)


class EventBus:
    """
    Event Bus síncrono que maneja la publicación y distribución de eventos.
    """

    def __init__(self, registry: EventHandlerRegistry, max_history: int = 0):
        self.registry = registry
        self.max_history = max_history
        self._history: deque = deque(maxlen=max_history if max_history > 0 else None)
        self._events_published = 0
        self._handlers_executed = 0
        self._handler_errors = 0

        logger.info(f"Event Bus inicializado con historial máximo de {self.max_history} eventos.")

    def publish(self, event: Event) -> None:
        """Publica un evento y lo distribuye a los manejadores registrados."""
        if not event:
            logger.warning("Intento de publicar un evento nulo.")
            return
        
        self._events_published += 1

        # Añadir al historial si está habilitado
        if self.max_history > 0:
            self._history.append(event)

        logger.debug(f"Publicando evento: {event.type} (#{self._events_published})")

        try:
            # Obtener handlers para este tipo de evento
            handlers = self.registry.get_handlers(event.type)

            logger.debug(f"Distribuyendo evento '{event.type}' a {len(handlers)} manejadores.")

            # Ejecutar cada handler
            for handler in handlers:
                try:
                    handler.handle(event)
                    self._handlers_executed += 1
                    logger.debug(f"Manejador '{handler.handler_name}' ejecutado para evento '{event.type}'.")

                except Exception as e:
                    self._handler_errors += 1
                    logger.error(f"Error en manejador '{handler.handler_name}' para evento '{event.type}': {str(e)}", exc_info=True)
                    # Continuar con el siguiente handler

        except HandlerNotFoundError:
            # No hay handlers registrados para este tipo de evento - no es un error
            logger.debug(f"No hay manejadores registrados para el evento '{event.type}'.")

        except Exception as e:
            logger.error(f"Error al publicar evento '{event.type}': {str(e)}", exc_info=True)

    def get_history(self) -> List[Event]:
        """Retorna el historial de eventos publicados."""
        return list(self._history)
    
    def get_stats(self) -> dict:
        """Retorna estadísticas del Event Bus."""
        return {
            'events_published': self._events_published,
            'handlers_executed': self._handlers_executed,
            'handler_errors': self._handler_errors,
            'history_size': len(self._history),
            'max_history': self.max_history,
        }
    
    def clear_history(self) -> None:
        """Limpia el historial de eventos."""
        self._history.clear()
        logger.debug("Historial de eventos limpiado.")

    def reset_stats(self) -> None:
        """Resetea las estadísticas del Event Bus."""
        self._events_published = 0
        self._handlers_executed = 0
        self._handler_errors = 0
        logger.debug("Estadísticas del Event Bus reseteadas.")

    def __str__(self) -> str:
        """Representación en cadena del Event Bus."""
        stats = self.get_stats()
        return (
            f"EventBus("
            f"events: {stats['events_published']}, "
            f"handlers: {stats['handlers_executed']}, "
            f"errors: {stats['handler_errors']}, "
            f"history: {stats['history_size']}/{stats['max_history']}"
            f")"
        )
    