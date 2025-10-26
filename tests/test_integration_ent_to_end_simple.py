"""
Test de integración end-to-end simple: Data → Signal → Order (simulado)
"""

from queue import Queue
from datetime import datetime
from typing import Optional
import pandas as pd

from data.historic_csv_data_handler import HistoricCSVDataHandler
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from models.events import MarketEvent, SignalEvent, OrderEvent
from models.enums import EventType, SignalType, OrderType, OrderDirection


class SimpleStrategyHandler(BaseEventHandler):
    """Handler que simula una estrategia simple: si close > open, genera LONG"""
    
    def __init__(self):
        super().__init__("SimpleStrategy")
        self.signals_generated = []
        self.events_queue: Optional[Queue[SignalEvent]] = None  # Se asignará externamente
    
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        if isinstance(event, MarketEvent) and event.data:
            open_price = event.data.get('open', 0)
            close_price = event.data.get('close', 0)
            
            # Estrategia simple: si close > open, generar señal LONG
            if close_price > open_price:
                signal = SignalEvent(
                    symbol=event.symbol,
                    timestamp=event.timestamp,
                    signal_type=SignalType.LONG
                )
                self.signals_generated.append(signal)
                
                # En un sistema real, esto iría al Event Bus
                if self.events_queue:
                    self.events_queue.put(signal)


class SimpleOrderHandler(BaseEventHandler):
    """Handler que convierte señales en órdenes"""
    
    def __init__(self):
        super().__init__("SimpleOrderManager")
        self.orders_created = []
    
    @property
    def supported_events(self):
        return {EventType.SIGNAL}
    
    def handle(self, event):
        if isinstance(event, SignalEvent):
            # Convertir señal a orden
            direction = OrderDirection.BUY if event.signal_type == SignalType.LONG else OrderDirection.SELL
            
            order = OrderEvent(
                symbol=event.symbol,
                timestamp=event.timestamp,
                order_type=OrderType.MARKET,
                quantity=0.1,
                direction=direction
            )
            self.orders_created.append(order)


def test_end_to_end_data_to_orders():
    """
    Test end-to-end: Datos → Estrategia → Señales → Órdenes
    """
    # Arrange: Datos que deberían generar señales LONG (close > open)
    df = pd.DataFrame({
        'open': [100.0, 102.0],
        'high': [105.0, 107.0],
        'low': [99.0, 101.0],
        'close': [104.0, 106.0],  # Ambos close > open
        'volume': [1000.0, 1100.0]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    
    # Setup componentes
    events_queue = Queue()
    data_handler = HistoricCSVDataHandler(events_queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    strategy = SimpleStrategyHandler()
    order_manager = SimpleOrderHandler()
    
    # Conectar strategy al queue para que pueda publicar señales
    strategy.events_queue = events_queue
    
    registry.register_handler(strategy)
    registry.register_handler(order_manager)
    
    # Act: Procesar todo el pipeline
    events_processed = 0
    while data_handler.continue_backtest and events_processed < 10:  # safety limit
        data_handler.update_bars()
        
        # Procesar todos los eventos en la cola
        while not events_queue.empty():
            event = events_queue.get_nowait()
            if registry.has_handlers(event.type):
                handlers = registry.get_handlers(event.type)
                for handler in handlers:
                    handler.handle(event)
        
        events_processed += 1
    
    # Assert: Verificar pipeline completo
    assert len(strategy.signals_generated) == 2, "Should generate 2 LONG signals"
    assert len(order_manager.orders_created) == 2, "Should create 2 BUY orders"
    
    # Verificar primera señal y orden
    first_signal = strategy.signals_generated[0]
    first_order = order_manager.orders_created[0]
    
    assert first_signal.symbol == "BTCUSDT"
    assert first_signal.signal_type == SignalType.LONG
    
    assert first_order.symbol == "BTCUSDT"
    assert first_order.direction == OrderDirection.BUY
    assert first_order.order_type == OrderType.MARKET
    assert first_order.quantity == 0.1


def test_no_signals_when_close_not_greater_than_open():
    """
    Test que no se generan señales cuando close <= open
    """
    # Arrange: Datos bajistas (close <= open)
    df = pd.DataFrame({
        'open': [100.0, 102.0],
        'close': [98.0, 102.0],  # close <= open
        'volume': [1000.0, 1100.0]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    
    events_queue = Queue()
    data_handler = HistoricCSVDataHandler(events_queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    strategy = SimpleStrategyHandler()
    strategy.events_queue = events_queue
    registry.register_handler(strategy)
    
    # Act
    while data_handler.continue_backtest:
        data_handler.update_bars()
        while not events_queue.empty():
            event = events_queue.get_nowait()
            if registry.has_handlers(event.type):
                handlers = registry.get_handlers(event.type)
                for handler in handlers:
                    handler.handle(event)
    
    # Assert: No signals generated
    assert len(strategy.signals_generated) == 0
