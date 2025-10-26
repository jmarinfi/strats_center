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

__all__ = [
    "EventBusError",
    "HandlerNotFoundError",
    "HandlerRegistrationError",
    "EventPublishError",
    "EventProcessingError",
    "EventBusConfigError",
]
