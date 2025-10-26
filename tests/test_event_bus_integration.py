"""
Tests de integración para EventBus con componentes reales.
"""

from queue import Queue
from datetime import datetime
import pandas as pd

from event_bus.event_bus import EventBus
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from data.historic_csv_data_handler import HistoricCSVDataHandler
from models.events import MarketEvent, SignalEvent
from models.enums import EventType, SignalType


class SimpleStrategyHandler(BaseEventHandler):
    """Estrategia simple que genera señales basada en precio."""
    
    def __init__(self, event_bus):
        super().__init__("SimpleStrategy")
        self.event_bus = event_bus
        self.signals_generated = []
    
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        if isinstance(event, MarketEvent) and event.data:
            close = event.data.get('close', 0)
            open_price = event.data.get('open', 0)
            
            # Estrategia: LONG si close > open + 2%
            if close > open_price * 1.02:
                signal = SignalEvent(
                    symbol=event.symbol,
                    timestamp=event.timestamp,
                    signal_type=SignalType.LONG
                )
                self.signals_generated.append(signal)
                self.event_bus.publish(signal)  # Re-publicar en el bus


def test_eventbus_with_data_handler_integration():
    """Test integración EventBus con HistoricCSVDataHandler."""
    # Setup datos
    df = pd.DataFrame({
        'open': [100.0, 102.0],
        'high': [105.0, 108.0],
        'low': [99.0, 101.0],
        'close': [104.0, 106.0],  # close > open * 1.02
        'volume': [1000.0, 1200.0]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    
    # Setup componentes
    queue = Queue()
    data_handler = HistoricCSVDataHandler(queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    event_bus = EventBus(registry, max_history=10)
    
    strategy = SimpleStrategyHandler(event_bus)
    registry.register_handler(strategy)
    
    # Simular BacktestEngine simple
    events_processed = 0
    while data_handler.continue_backtest and events_processed < 5:
        # Data handler genera MarketEvent
        data_handler.update_bars()
        
        # EventBus procesa eventos de la cola
        while not queue.empty():
            event = queue.get_nowait()
            event_bus.publish(event)  # EventBus dispatch
        
        events_processed += 1
    
    # Assert integración completa
    assert len(strategy.signals_generated) == 2  # Dos señales LONG
    
    # Verificar estadísticas del EventBus
    stats = event_bus.get_stats()
    assert stats['events_published'] == 4  # 2 MarketEvent + 2 SignalEvent
    assert stats['handlers_executed'] == 2  # Solo strategy maneja MARKET
    assert stats['handler_errors'] == 0
    
    # Verificar historial
    history = event_bus.get_history()
    assert len(history) == 4
    
    # CORRECCIÓN: Orden real es intercalado (síncrono)
    # MarketEvent1 → SignalEvent1 → MarketEvent2 → SignalEvent2
    assert history[0].type == EventType.MARKET   # Primera barra
    assert history[1].type == EventType.SIGNAL   # Señal de primera barra
    assert history[2].type == EventType.MARKET   # Segunda barra  
    assert history[3].type == EventType.SIGNAL   # Señal de segunda barra
    
    # Verificar que ambos tipos de eventos están presentes
    market_events = [e for e in history if e.type == EventType.MARKET]
    signal_events = [e for e in history if e.type == EventType.SIGNAL]
    
    assert len(market_events) == 2
    assert len(signal_events) == 2
    
    # Verificar símbolos correctos
    assert all(e.symbol == "BTCUSDT" for e in history)
    assert all(e.signal_type == SignalType.LONG for e in signal_events)


def test_eventbus_error_isolation():
    """Test que EventBus aísla errores entre handlers."""
    registry = EventHandlerRegistry()
    event_bus = EventBus(registry)
    
    # Handler bueno
    good_handler = SimpleStrategyHandler(event_bus)
    
    # Handler malo que falla
    class BadHandler(BaseEventHandler):
        def __init__(self):
            super().__init__("BadHandler")
        
        @property
        def supported_events(self):
            return {EventType.MARKET}
        
        def handle(self, event):
            raise Exception("Handler falló!")
    
    bad_handler = BadHandler()
    
    registry.register_handler(good_handler)
    registry.register_handler(bad_handler)
    
    # Publicar evento que genera señal
    event = MarketEvent(
        symbol="TEST",
        timestamp=datetime.now(),
        data={'open': 100, 'close': 103}  # close > open * 1.02, genera señal
    )
    
    event_bus.publish(event)
    
    # Assert: handler bueno funcionó, malo falló pero no tumbó sistema
    assert len(good_handler.signals_generated) == 1  # Handler bueno funcionó
    
    stats = event_bus.get_stats()
    assert stats['events_published'] == 2  # MarketEvent + SignalEvent
    assert stats['handlers_executed'] == 1  # Solo good_handler para MARKET
    assert stats['handler_errors'] == 1    # bad_handler falló


def test_eventbus_no_signal_generation():
    """Test que no se generan señales cuando no se cumple condición."""
    # Setup datos que NO generan señales (close <= open * 1.02)
    df = pd.DataFrame({
        'open': [100.0, 102.0],
        'high': [105.0, 108.0],
        'low': [99.0, 101.0],
        'close': [101.0, 103.0],  # close <= open * 1.02
        'volume': [1000.0, 1200.0]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    
    # Setup componentes
    queue = Queue()
    data_handler = HistoricCSVDataHandler(queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    event_bus = EventBus(registry, max_history=5)
    
    strategy = SimpleStrategyHandler(event_bus)
    registry.register_handler(strategy)
    
    # Simular BacktestEngine
    events_processed = 0
    while data_handler.continue_backtest and events_processed < 5:
        data_handler.update_bars()
        
        while not queue.empty():
            event = queue.get_nowait()
            event_bus.publish(event)
        
        events_processed += 1
    
    # Assert: no se generaron señales
    assert len(strategy.signals_generated) == 0
    
    # Solo MarketEvents en el historial
    stats = event_bus.get_stats()
    assert stats['events_published'] == 2  # Solo 2 MarketEvent
    assert stats['handlers_executed'] == 2  # Strategy ejecutado 2 veces
    assert stats['handler_errors'] == 0
    
    history = event_bus.get_history()
    assert len(history) == 2
    assert all(e.type == EventType.MARKET for e in history)


def test_eventbus_multiple_strategies():
    """Test EventBus con múltiples estrategias que generan señales."""
    # Setup
    df = pd.DataFrame({
        'open': [100.0],
        'close': [105.0],  # Genera señal
        'volume': [1000.0]
    }, index=[pd.Timestamp('2023-01-01')])
    
    queue = Queue()
    data_handler = HistoricCSVDataHandler(queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    event_bus = EventBus(registry, max_history=10)
    
    # Dos estrategias diferentes
    strategy1 = SimpleStrategyHandler(event_bus)
    
    class Strategy2(BaseEventHandler):
        def __init__(self, event_bus):
            super().__init__("Strategy2")
            self.event_bus = event_bus
            self.signals_generated = []
        
        @property
        def supported_events(self):
            return {EventType.MARKET}
        
        def handle(self, event):
            if isinstance(event, MarketEvent) and event.data:
                # Estrategia diferente: SHORT si volume > 500
                volume = event.data.get('volume', 0)
                if volume > 500:
                    signal = SignalEvent(
                        symbol=event.symbol,
                        timestamp=event.timestamp,
                        signal_type=SignalType.SHORT
                    )
                    self.signals_generated.append(signal)
                    self.event_bus.publish(signal)
    
    strategy2 = Strategy2(event_bus)
    
    registry.register_handler(strategy1)
    registry.register_handler(strategy2)
    
    # Procesar datos
    data_handler.update_bars()
    while not queue.empty():
        event = queue.get_nowait()
        event_bus.publish(event)
    
    # Assert: ambas estrategias generaron señales
    assert len(strategy1.signals_generated) == 1  # LONG
    assert len(strategy2.signals_generated) == 1  # SHORT
    assert strategy1.signals_generated[0].signal_type == SignalType.LONG
    assert strategy2.signals_generated[0].signal_type == SignalType.SHORT
    
    # Verificar historial: 1 MarketEvent + 2 SignalEvents
    stats = event_bus.get_stats()
    assert stats['events_published'] == 3
    assert stats['handlers_executed'] == 2  # Ambas estrategias para MARKET
    
    history = event_bus.get_history()
    assert len(history) == 3
    assert history[0].type == EventType.MARKET
    # Los siguientes 2 pueden ser en cualquier orden (ambos SIGNAL)
    signal_events = [e for e in history[1:] if e.type == EventType.SIGNAL]
    assert len(signal_events) == 2
    
    signal_types = {e.signal_type for e in signal_events}
    assert SignalType.LONG in signal_types
    assert SignalType.SHORT in signal_types
