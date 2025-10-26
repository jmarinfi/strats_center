"""
Event Bus package exports its exceptions for external use.
"""

from .exceptions import (
    EventBusError,
    HandlerNotFoundError,
    HandlerRegistrationError,
    EventPublishError,
    EventProcessingError,
    EventBusConfigError,
)
from .handlers import (
    IEventHandler,
    EventHandlerRegistry,
    BaseEventHandler,
    create_function_handler,
)

__all__ = [
    # Exceptions
    "EventBusError",
    "HandlerNotFoundError",
    "HandlerRegistrationError",
    "EventPublishError",
    "EventProcessingError",
    "EventBusConfigError",
    # Handlers
    "IEventHandler",
    "EventHandlerRegistry",
    "BaseEventHandler",
    "create_function_handler",
]
