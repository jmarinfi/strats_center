from enum import Enum
from datetime import datetime

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
    

class SignalEvent(Event):
    """
    Maneja el envío de una señal desde un objeto Strategy.
    """
    type: EventType = EventType.SIGNAL
    symbol: str
    date: datetime
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


class FillEvent(Event):
    """
    Encapsula la noción de una orden que ha sido ejecutada.
    """
    type: EventType = EventType.FILL
    timeindex: datetime
    symbol: str
    exchange: str
    quantity: float
    direction: OrderDirection
    fill_cost: float
    commission: float
