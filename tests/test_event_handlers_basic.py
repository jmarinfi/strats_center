import pytest
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from event_bus.exceptions import HandlerNotFoundError
from models.enums import EventType

class HMarket(BaseEventHandler):
    @property
    def supported_events(self):
        return {EventType.MARKET}
    def handle(self, event):  # no-op
        return

class HSignal(BaseEventHandler):
    @property
    def supported_events(self):
        return {EventType.SIGNAL}
    def handle(self, event):
        return

class HMulti(BaseEventHandler):
    @property
    def supported_events(self):
        return {EventType.MARKET, EventType.SIGNAL, EventType.FILL}
    def handle(self, event):
        return

def test_registry_starts_empty():
    reg = EventHandlerRegistry()
    assert reg.get_all_registered_events() == set()
    assert reg.get_handler_count(EventType.MARKET) == 0

def test_register_single_handler():
    reg = EventHandlerRegistry()
    h = HMarket()
    reg.register_handler(h)
    assert reg.has_handlers(EventType.MARKET)
    assert reg.get_handler_count(EventType.MARKET) == 1
    assert reg.get_handlers(EventType.MARKET)[0] is h

def test_register_multiple_handlers_same_event():
    reg = EventHandlerRegistry()
    h1, h2 = HMarket(), HMarket()
    reg.register_handler(h1)
    reg.register_handler(h2)
    hs = reg.get_handlers(EventType.MARKET)
    assert len(hs) == 2 and h1 in hs and h2 in hs

def test_register_handlers_different_events():
    reg = EventHandlerRegistry()
    hm, hs = HMarket(), HSignal()
    reg.register_handler(hm); reg.register_handler(hs)
    assert reg.has_handlers(EventType.MARKET)
    assert reg.has_handlers(EventType.SIGNAL)
    assert reg.get_handler_count(EventType.FILL) == 0

def test_register_multi_event_handler():
    reg = EventHandlerRegistry()
    h = HMulti()
    reg.register_handler(h)
    assert reg.has_handlers(EventType.MARKET)
    assert reg.has_handlers(EventType.SIGNAL)
    assert reg.has_handlers(EventType.FILL)
    assert reg.get_handler_count(EventType.ORDER) == 0
    for et in (EventType.MARKET, EventType.SIGNAL, EventType.FILL):
        assert h in reg.get_handlers(et)

def test_unregister_handler_across_events():
    reg = EventHandlerRegistry()
    h = HMulti()
    reg.register_handler(h)
    reg.unregister_handler(h)
    for et in (EventType.MARKET, EventType.SIGNAL, EventType.FILL):
        assert not reg.has_handlers(et)

def test_get_handlers_for_empty_event_raises():
    reg = EventHandlerRegistry()
    with pytest.raises(HandlerNotFoundError):
        reg.get_handlers(EventType.ORDER)

def test_clear_registry():
    reg = EventHandlerRegistry()
    reg.register_handler(HMarket())
    reg.register_handler(HSignal())
    reg.clear()
    assert reg.get_all_registered_events() == set()
    for et in (EventType.MARKET, EventType.SIGNAL, EventType.FILL, EventType.ORDER):
        assert reg.get_handler_count(et) == 0

def test_registry_str_contains_registered_classes():
    reg = EventHandlerRegistry()
    hm, hmu = HMarket(), HMulti()
    reg.register_handler(hm)
    reg.register_handler(hmu)
    s = str(reg)
    # La implementación actual imprime "EventHandlerRegistry:" (sin ' Handler ')
    assert "EventHandlerRegistry" in s
    assert "MARKET" in s
    assert "HMarket" in s
    assert "HMulti" in s
