"""
Tests para EventBus del sistema de trading.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from event_bus.event_bus import EventBus
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from models.events import MarketEvent, SignalEvent, ErrorEvent
from models.enums import EventType, SignalType


class MockEventHandler(BaseEventHandler):
    """Handler de prueba que cuenta eventos recibidos."""
    
    def __init__(self, supported_event_types, name=None):
        super().__init__(name)
        self._supported_event_types = supported_event_types
        self.events_received = []
        self.call_count = 0
        
    @property
    def supported_events(self):
        return self._supported_event_types
    
    def handle(self, event):
        self.call_count += 1
        self.events_received.append(event)


class FaultyHandler(BaseEventHandler):
    """Handler que siempre falla para testing de tolerancia a errores."""
    
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        raise ValueError("Handler simulado que falla")


class TestEventBus:
    """Tests para EventBus."""
    
    def setup_method(self):
        """Setup antes de cada test."""
        self.registry = EventHandlerRegistry()
        self.event_bus = EventBus(self.registry)
    
    def test_eventbus_initialization(self):
        """Test inicialización básica del EventBus."""
        bus = EventBus(self.registry, max_history=10)
        
        assert bus.registry == self.registry
        assert bus.max_history == 10
        assert bus.get_history() == []
        
        stats = bus.get_stats()
        assert stats['events_published'] == 0
        assert stats['handlers_executed'] == 0
        assert stats['handler_errors'] == 0
        assert stats['max_history'] == 10
    
    def test_publish_single_handler(self):
        """Test publicar evento con un solo handler."""
        # Setup
        handler = MockEventHandler({EventType.MARKET}, "TestMarketHandler")
        self.registry.register_handler(handler)
        
        event = MarketEvent(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            data={"open": 100, "close": 105}
        )
        
        # Act
        self.event_bus.publish(event)
        
        # Assert
        assert handler.call_count == 1
        assert len(handler.events_received) == 1
        assert handler.events_received[0] == event
        
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 1
        assert stats['handlers_executed'] == 1
        assert stats['handler_errors'] == 0
    
    def test_publish_multiple_handlers_same_event(self):
        """Test que múltiples handlers reciben el mismo evento."""
        # Setup
        handler1 = MockEventHandler({EventType.MARKET}, "Handler1")
        handler2 = MockEventHandler({EventType.MARKET}, "Handler2")
        
        self.registry.register_handler(handler1)
        self.registry.register_handler(handler2)
        
        event = MarketEvent(
            symbol="ETHUSD",
            timestamp=datetime.now(),
            data={"close": 200}
        )
        
        # Act
        self.event_bus.publish(event)
        
        # Assert
        assert handler1.call_count == 1
        assert handler2.call_count == 1
        assert handler1.events_received[0] == event
        assert handler2.events_received[0] == event
        
        stats = self.event_bus.get_stats()
        assert stats['handlers_executed'] == 2
    
    def test_publish_no_handlers(self):
        """Test publicar evento sin handlers registrados (no debe fallar)."""
        event = SignalEvent(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            signal_type=SignalType.LONG
        )
        
        # Act - no debe lanzar excepción
        self.event_bus.publish(event)
        
        # Assert
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 1
        assert stats['handlers_executed'] == 0
        assert stats['handler_errors'] == 0
    
    def test_publish_none_event(self):
        """Test publicar evento None."""
        handler = MockEventHandler({EventType.MARKET})
        self.registry.register_handler(handler)
        
        # Act
        self.event_bus.publish(None)
        
        # Assert - handler no debe ejecutarse
        assert handler.call_count == 0
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 0
    
    def test_handler_error_tolerance(self):
        """Test que errores en handlers no tumban el sistema."""
        # Setup: handler normal y handler que falla
        good_handler = MockEventHandler({EventType.MARKET}, "GoodHandler")
        faulty_handler = FaultyHandler()
        
        self.registry.register_handler(good_handler)
        self.registry.register_handler(faulty_handler)
        
        event = MarketEvent(
            symbol="BTCUSDT",
            timestamp=datetime.now(),
            data={"close": 100}
        )
        
        # Act
        self.event_bus.publish(event)
        
        # Assert - handler bueno debe ejecutarse, el malo fallar sin tumbar sistema
        assert good_handler.call_count == 1
        assert good_handler.events_received[0] == event
        
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 1
        assert stats['handlers_executed'] == 1  # Solo el handler bueno
        assert stats['handler_errors'] == 1     # El handler malo falló
    
    def test_event_history_disabled(self):
        """Test EventBus sin historial (max_history=0)."""
        bus = EventBus(self.registry, max_history=0)
        
        event = MarketEvent(symbol="TEST", timestamp=datetime.now())
        bus.publish(event)
        
        assert bus.get_history() == []
        assert bus.get_stats()['max_history'] == 0
    
    def test_event_history_enabled(self):
        """Test EventBus con historial habilitado."""
        bus = EventBus(self.registry, max_history=3)
        
        events = []
        for i in range(3):
            event = MarketEvent(
                symbol=f"TEST{i}",
                timestamp=datetime.now(),
                data={"price": i * 100}
            )
            events.append(event)
            bus.publish(event)
        
        history = bus.get_history()
        assert len(history) == 3
        assert history == events
    
    def test_event_history_max_size(self):
        """Test que el historial respeta el tamaño máximo."""
        bus = EventBus(self.registry, max_history=2)
        
        # Publicar 3 eventos (más que el máximo)
        events = []
        for i in range(3):
            event = MarketEvent(
                symbol=f"TEST{i}",
                timestamp=datetime.now(),
                data={"id": i}
            )
            events.append(event)
            bus.publish(event)
        
        history = bus.get_history()
        assert len(history) == 2  # Solo mantiene los últimos 2
        assert history == events[1:]  # Los últimos 2 eventos
    
    def test_clear_history(self):
        """Test limpiar historial."""
        bus = EventBus(self.registry, max_history=5)
        
        # Añadir eventos al historial
        for i in range(3):
            event = MarketEvent(symbol=f"TEST{i}", timestamp=datetime.now())
            bus.publish(event)
        
        assert len(bus.get_history()) == 3
        
        # Limpiar historial
        bus.clear_history()
        assert bus.get_history() == []
    
    def test_reset_stats(self):
        """Test reiniciar estadísticas."""
        handler = MockEventHandler({EventType.MARKET})
        self.registry.register_handler(handler)
        
        # Generar actividad
        event = MarketEvent(symbol="TEST", timestamp=datetime.now())
        self.event_bus.publish(event)
        
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 1
        assert stats['handlers_executed'] == 1
        
        # Resetear estadísticas
        self.event_bus.reset_stats()
        
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 0
        assert stats['handlers_executed'] == 0
        assert stats['handler_errors'] == 0
    
    def test_different_event_types(self):
        """Test manejo de diferentes tipos de eventos."""
        # Setup handlers para diferentes tipos
        market_handler = MockEventHandler({EventType.MARKET}, "MarketHandler")
        signal_handler = MockEventHandler({EventType.SIGNAL}, "SignalHandler")
        error_handler = MockEventHandler({EventType.ERROR}, "ErrorHandler")
        
        self.registry.register_handler(market_handler)
        self.registry.register_handler(signal_handler)
        self.registry.register_handler(error_handler)
        
        # Crear eventos diferentes
        market_event = MarketEvent(symbol="BTC", timestamp=datetime.now())
        signal_event = SignalEvent(symbol="ETH", timestamp=datetime.now(), signal_type=SignalType.SHORT)
        error_event = ErrorEvent(
            timestamp=datetime.now(),
            source="test",
            error_type="TestError",
            message="Test error"
        )
        
        # Publicar eventos
        self.event_bus.publish(market_event)
        self.event_bus.publish(signal_event)
        self.event_bus.publish(error_event)
        
        # Assert - cada handler solo recibe sus eventos
        assert market_handler.call_count == 1
        assert signal_handler.call_count == 1
        assert error_handler.call_count == 1
        
        assert market_handler.events_received[0] == market_event
        assert signal_handler.events_received[0] == signal_event
        assert error_handler.events_received[0] == error_event
        
        stats = self.event_bus.get_stats()
        assert stats['events_published'] == 3
        assert stats['handlers_executed'] == 3
    
    def test_string_representation(self):
        """Test representación string del EventBus."""
        bus = EventBus(self.registry, max_history=10)
        
        handler = MockEventHandler({EventType.MARKET})
        self.registry.register_handler(handler)
        
        # Estado inicial
        str_repr = str(bus)
        assert "events: 0" in str_repr
        assert "handlers: 0" in str_repr
        assert "errors: 0" in str_repr
        assert "history: 0/10" in str_repr
        
        # Después de publicar evento
        event = MarketEvent(symbol="TEST", timestamp=datetime.now())
        bus.publish(event)
        
        str_repr = str(bus)
        assert "events: 1" in str_repr
        assert "handlers: 1" in str_repr
        assert "history: 1/10" in str_repr
