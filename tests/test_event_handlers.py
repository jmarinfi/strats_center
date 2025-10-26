"""
Tests básicos para registro de handlers del Event Bus.
Solo testea funcionalidad de registro, sin eventos complejos.
"""

import pytest
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from event_bus.exceptions import HandlerRegistrationError, HandlerNotFoundError
from models.enums import EventType


class SimpleMarketHandler(BaseEventHandler):
    """Handler simple que solo maneja eventos MARKET."""
    
    def __init__(self):
        super().__init__("SimpleMarketHandler")
        self.call_count = 0
    
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        self.call_count += 1
        print(f"SimpleMarketHandler manejó un evento")


class SimpleSignalHandler(BaseEventHandler):
    """Handler simple que solo maneja eventos SIGNAL."""
    
    def __init__(self):
        super().__init__("SimpleSignalHandler")
        self.call_count = 0
    
    @property
    def supported_events(self):
        return {EventType.SIGNAL}
    
    def handle(self, event):
        self.call_count += 1
        print(f"SimpleSignalHandler manejó un evento")


class MultiEventHandler(BaseEventHandler):
    """Handler que maneja múltiples tipos de eventos."""
    
    def __init__(self):
        super().__init__("MultiEventHandler")
        self.call_count = 0
    
    @property
    def supported_events(self):
        return {EventType.MARKET, EventType.SIGNAL, EventType.FILL}
    
    def handle(self, event):
        self.call_count += 1
        print(f"MultiEventHandler manejó un evento de tipo {event.type}")


class TestBasicHandlerRegistration:
    """Tests básicos para registro de handlers."""
    
    def setup_method(self):
        """Setup antes de cada test."""
        self.registry = EventHandlerRegistry()
    
    def test_registry_starts_empty(self):
        """Test que el registry empieza vacío."""
        assert len(self.registry.get_all_registered_events()) == 0
        assert not self.registry.has_handlers(EventType.MARKET)
        assert not self.registry.has_handlers(EventType.SIGNAL)
        assert self.registry.get_handler_count(EventType.MARKET) == 0
    
    def test_register_single_handler(self):
        """Test registrar un handler para un solo evento."""
        handler = SimpleMarketHandler()
        
        # Registrar
        self.registry.register_handler(handler)
        
        # Verificar registro
        assert self.registry.has_handlers(EventType.MARKET)
        assert not self.registry.has_handlers(EventType.SIGNAL)
        assert self.registry.get_handler_count(EventType.MARKET) == 1
        assert self.registry.get_handler_count(EventType.SIGNAL) == 0
        
        # Verificar que podemos obtener el handler
        handlers = self.registry.get_handlers(EventType.MARKET)
        assert len(handlers) == 1
        assert handlers[0] == handler
        
        # Verificar eventos registrados
        registered_events = self.registry.get_all_registered_events()
        assert EventType.MARKET in registered_events
        assert EventType.SIGNAL not in registered_events
    
    def test_register_multiple_handlers_same_event(self):
        """Test registrar múltiples handlers para el mismo evento."""
        handler1 = SimpleMarketHandler()
        handler2 = SimpleMarketHandler()  # Otro handler para MARKET
        
        # Registrar ambos
        self.registry.register_handler(handler1)
        self.registry.register_handler(handler2)
        
        # Verificar que ambos están registrados
        assert self.registry.get_handler_count(EventType.MARKET) == 2
        
        handlers = self.registry.get_handlers(EventType.MARKET)
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers
    
    def test_register_handlers_different_events(self):
        """Test registrar handlers para diferentes eventos."""
        market_handler = SimpleMarketHandler()
        signal_handler = SimpleSignalHandler()
        
        # Registrar handlers
        self.registry.register_handler(market_handler)
        self.registry.register_handler(signal_handler)
        
        # Verificar registros independientes
        assert self.registry.has_handlers(EventType.MARKET)
        assert self.registry.has_handlers(EventType.SIGNAL)
        assert self.registry.get_handler_count(EventType.MARKET) == 1
        assert self.registry.get_handler_count(EventType.SIGNAL) == 1
        
        # Verificar handlers correctos
        market_handlers = self.registry.get_handlers(EventType.MARKET)
        signal_handlers = self.registry.get_handlers(EventType.SIGNAL)
        
        assert len(market_handlers) == 1
        assert len(signal_handlers) == 1
        assert market_handlers[0] == market_handler
        assert signal_handlers[0] == signal_handler
    
    def test_register_multi_event_handler(self):
        """Test registrar handler que maneja múltiples eventos."""
        handler = MultiEventHandler()
        
        # Registrar
        self.registry.register_handler(handler)
        
        # Verificar que está registrado para todos sus eventos
        assert self.registry.has_handlers(EventType.MARKET)
        assert self.registry.has_handlers(EventType.SIGNAL)
        assert self.registry.has_handlers(EventType.FILL)
        assert not self.registry.has_handlers(EventType.ORDER)  # No soporta ORDER
        
        # Verificar counts
        assert self.registry.get_handler_count(EventType.MARKET) == 1
        assert self.registry.get_handler_count(EventType.SIGNAL) == 1
        assert self.registry.get_handler_count(EventType.FILL) == 1
        assert self.registry.get_handler_count(EventType.ORDER) == 0
        
        # Verificar que el mismo handler está en todas las listas
        market_handlers = self.registry.get_handlers(EventType.MARKET)
        signal_handlers = self.registry.get_handlers(EventType.SIGNAL)
        fill_handlers = self.registry.get_handlers(EventType.FILL)
        
        assert handler in market_handlers
        assert handler in signal_handlers  
        assert handler in fill_handlers
    
    def test_unregister_handler(self):
        """Test desregistrar un handler."""
        handler = SimpleMarketHandler()
        
        # Registrar
        self.registry.register_handler(handler)
        assert self.registry.has_handlers(EventType.MARKET)
        
        # Desregistrar
        self.registry.unregister_handler(handler)
        assert not self.registry.has_handlers(EventType.MARKET)
        assert self.registry.get_handler_count(EventType.MARKET) == 0
    
    def test_unregister_multi_event_handler(self):
        """Test desregistrar handler que maneja múltiples eventos."""
        handler = MultiEventHandler()
        
        # Registrar
        self.registry.register_handler(handler)
        assert self.registry.has_handlers(EventType.MARKET)
        assert self.registry.has_handlers(EventType.SIGNAL)
        assert self.registry.has_handlers(EventType.FILL)
        
        # Desregistrar
        self.registry.unregister_handler(handler)
        
        # Verificar que se removió de todos los eventos
        assert not self.registry.has_handlers(EventType.MARKET)
        assert not self.registry.has_handlers(EventType.SIGNAL)
        assert not self.registry.has_handlers(EventType.FILL)
    
    def test_get_handlers_for_nonexistent_event(self):
        """Test obtener handlers para evento sin handlers registrados."""
        with pytest.raises(HandlerNotFoundError):
            self.registry.get_handlers(EventType.ORDER)
    
    def test_clear_registry(self):
        """Test limpiar todo el registry."""
        # Registrar algunos handlers
        self.registry.register_handler(SimpleMarketHandler())
        self.registry.register_handler(SimpleSignalHandler())
        self.registry.register_handler(MultiEventHandler())
        
        # Verificar que hay handlers
        assert len(self.registry.get_all_registered_events()) > 0
        assert self.registry.has_handlers(EventType.MARKET)
        
        # Limpiar
        self.registry.clear()
        
        # Verificar que está vacío
        assert len(self.registry.get_all_registered_events()) == 0
        assert not self.registry.has_handlers(EventType.MARKET)
        assert not self.registry.has_handlers(EventType.SIGNAL)
    
    def test_registry_string_representation(self):
        """Test que el registry tiene representación string."""
        handler1 = SimpleMarketHandler()
        handler2 = MultiEventHandler()
        
        self.registry.register_handler(handler1)
        self.registry.register_handler(handler2)
        
        registry_str = str(self.registry)
        
        # Verificar que contiene información básica
        assert "Event Handler Registry" in registry_str
        assert "MARKET" in registry_str
        assert "SimpleMarketHandler" in registry_str
        assert "MultiEventHandler" in registry_str


if __name__ == "__main__":
    # Ejecutar solo estos tests
    pytest.main([__file__, "-v"])
