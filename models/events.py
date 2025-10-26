from enum import Enum
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from models.enums import EventType, SignalType, OrderType, OrderDirection


class Event(BaseModel):
    """
    Clase base para todos los eventos en el sistema de trading.
    """
    type: EventType


class MarketEvent(Event):
    """
    Indica una nueva actualización de datos de mercado.
    """
    type: EventType = EventType.MARKET
    symbol: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    

class SignalEvent(Event):
    """
    Maneja el envío de una señal desde un objeto Strategy.
    """
    type: EventType = EventType.SIGNAL
    symbol: str
    timestamp: datetime
    signal_type: SignalType


class OrderEvent(Event):
    """
    Maneja el envío de una orden a un sistema de ejecución.
    """
    type: EventType = EventType.ORDER
    symbol: str
    order_type: OrderType
    quantity: float
    direction: OrderDirection
    timestamp: datetime
    price: Optional[float] = None


class FillEvent(Event):
    """
    Encapsula la noción de una orden que ha sido ejecutada.
    """
    type: EventType = EventType.FILL
    timestamp: datetime
    symbol: str
    exchange: str
    quantity: float
    direction: OrderDirection
    fill_cost: float
    commission: float


class PortfolioEvent(Event):
    """
    Evento para actualizaciones de portafolio.
    """
    type: EventType = EventType.PORTFOLIO
    timestamp: datetime
    total_value: float
    cash: float
    positions: Dict[str, float]


class BacktestEvent(Event):
    """
    Evento específico para backtesting.
    """
    type: EventType = EventType.BACKTEST
    action: str # "start", "stop", "pause", "resume"
    timestamp: datetime
    message: Optional[str] = None


class ErrorEvent(Event):
    """
    Evento para reportar errores en el sistema.
    """
    type: EventType = EventType.ERROR
    timestamp: datetime
    source: str
    error_type: str
    message: str
    details: Optional[Dict] = None
