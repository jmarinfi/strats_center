from typing import Optional
from pydantic import BaseModel, ConfigDict

from models.enums import OrderDirection, OrderStatus, OrderType


model_config = ConfigDict(frozen=True)


class Ticker(BaseModel):
    """Representa el estado del ticker de un símbolo."""
    model_config = model_config

    symbol: str
    timestamp: int # timestamp in milliseconds
    last: float
    bid: float
    ask: float
    volume: float


class Balance(BaseModel):
    """Representa el balance de la cuenta."""
    model_config = model_config

    asset: str
    free: float
    used: float
    total: float


class Order(BaseModel):
    """Representa el estado de una orden."""
    model_config = model_config

    symbol: str
    order_id: str
    client_order_id: Optional[str] = None
    timestamp: int # timestamp in milliseconds
    status: OrderStatus
    type: OrderType
    side: OrderDirection
    quantity: float
    price: Optional[float] = None
    filled_quantity: float = 0.0
    average_price: Optional[float] = None
    commission: Optional[float] = None
    commission_asset: Optional[str] = None
    update_time: Optional[int] = None # timestamp in milliseconds