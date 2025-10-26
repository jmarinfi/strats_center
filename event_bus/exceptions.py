from typing import Optional


class EventBusError(Exception):
    """Excepción base para errores relacionados con el Event Bus."""
    pass


class HandlerNotFoundError(EventBusError):
    """Excepción lanzada cuando no se encuentra un manejador de eventos."""

    def __init__(self, event_type: str) -> None:
        super().__init__(f"No se encontró un manejador para el evento: {event_type}")


class HandlerRegistrationError(EventBusError):
    """Excepción lanzada cuando hay un error al registrar un manejador de eventos."""

    def __init(self, event_type: str, handler_name: str, reason: str) -> None:
        self.event_type = event_type
        self.handler_name = handler_name
        self.reason = reason
        super().__init__(f"Error al registrar el manejador '{handler_name}' para el evento '{event_type}': {reason}")


class EventPublishError(EventBusError):
    """Excepción lanzada cuando hay un error al publicar un evento."""

    def __init__(self, event_type: str, reason: str, original_exception: Optional[Exception] = None) -> None:
        self.event_type = event_type
        self.reason = reason
        self.original_exception = original_exception
        message = f"Error al publicar el evento '{event_type}': {reason}"
        if original_exception:
            message += f" | Excepción original: {str(original_exception)}"
        super().__init__(message)


class EventProcessingError(EventBusError):
    """Excepción lanzada cuando hay un error al procesar un evento."""

    def __init__(self, event_type: str, handler_name: str, reason: str, original_exception: Optional[Exception] = None) -> None:
        self.event_type = event_type
        self.handler_name = handler_name
        self.reason = reason
        self.original_exception = original_exception
        message = f"Error al procesar el evento '{event_type}' en el manejador '{handler_name}': {reason}"
        if original_exception:
            message += f" | Excepción original: {str(original_exception)}"
        super().__init__(message)


class EventBusConfigError(EventBusError):
    """Excepción lanzada cuando hay un error en la configuración del Event Bus."""
    
    def __init__(self, config_key: str, reason: str) -> None:
        self.config_key = config_key
        self.reason = reason
        super().__init__(f"Error de configuración en '{config_key}': {reason}")
        