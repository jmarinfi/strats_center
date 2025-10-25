import pytest
from datetime import datetime
from models.events import Event, MarketEvent, SignalEvent, OrderEvent, FillEvent
from models.enums import EventType, SignalType, OrderType, OrderDirection

def test_event_base():
    event = Event(type=EventType.MARKET)
    assert event.type == EventType.MARKET

def test_market_event():
    event = MarketEvent()
    assert event.type == EventType.MARKET

def test_signal_event():
    event = SignalEvent(type=EventType.SIGNAL, symbol="BTCUSDT", date=datetime(2023,1,1), signal_type=SignalType.LONG)
    assert event.type == EventType.SIGNAL
    assert event.symbol == "BTCUSDT"
    assert event.signal_type == SignalType.LONG

def test_order_event():
    event = OrderEvent(type=EventType.ORDER, symbol="BTCUSDT", order_type=OrderType.LIMIT, quantity=1.5, direction=OrderDirection.BUY)
    assert event.type == EventType.ORDER
    assert event.symbol == "BTCUSDT"
    assert event.order_type == OrderType.LIMIT
    assert event.quantity == 1.5
    assert event.direction == OrderDirection.BUY

def test_fill_event():
    event = FillEvent(type=EventType.FILL, timeindex=datetime(2023,1,1), symbol="BTCUSDT", exchange="Binance", quantity=2.0, direction=OrderDirection.SELL, fill_cost=100.0, commission=0.1)
    assert event.type == EventType.FILL
    assert event.symbol == "BTCUSDT"
    assert event.exchange == "Binance"
    assert event.quantity == 2.0
    assert event.direction == OrderDirection.SELL
    assert event.fill_cost == 100.0
    assert event.commission == 0.1
