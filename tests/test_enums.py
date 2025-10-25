import pytest
from models.enums import EventType, SignalType, OrderType, OrderDirection

def test_event_type_enum():
    assert EventType.MARKET == "MARKET"
    assert EventType.SIGNAL == "SIGNAL"
    assert EventType.ORDER == "ORDER"
    assert EventType.FILL == "FILL"

def test_signal_type_enum():
    assert SignalType.LONG == "LONG"
    assert SignalType.SHORT == "SHORT"
    assert SignalType.EXIT == "EXIT"

def test_order_type_enum():
    assert OrderType.MARKET == "MARKET"
    assert OrderType.LIMIT == "LIMIT"

def test_order_direction_enum():
    assert OrderDirection.BUY == "BUY"
    assert OrderDirection.SELL == "SELL"
