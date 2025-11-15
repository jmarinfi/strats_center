from enum import Enum


class EventType(str, Enum):
    """Enum para los tipos de eventos en el sistema de trading."""
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"
    PORTFOLIO = "PORTFOLIO"
    BACKTEST = "BACKTEST"
    ERROR = "ERROR"


class SignalType(str, Enum):
    """Enum para los tipos de señales de trading."""
    LONG = "LONG"
    SHORT = "SHORT"
    EXIT = "EXIT"


class OrderType(str, Enum):
    """Enum para los tipos de órdenes de trading."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderDirection(str, Enum):
    """Enum para las direcciones de las órdenes de trading."""
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    """Estado de una orden de trading."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    