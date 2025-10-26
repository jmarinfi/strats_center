"""
Test de integración: HistoricCSVDataHandler → MarketEvent → EventHandlerRegistry → Handler
"""

from queue import Queue
from datetime import datetime
import pandas as pd

from data.historic_csv_data_handler import HistoricCSVDataHandler
from event_bus.handlers import EventHandlerRegistry, BaseEventHandler
from models.events import MarketEvent
from models.enums import EventType


class SimpleMarketEventCounter(BaseEventHandler):
    """Handler que cuenta eventos de mercado recibidos."""
    
    def __init__(self):
        super().__init__("MarketEventCounter")
        self.events_received = []
        self.count = 0
    
    @property
    def supported_events(self):
        return {EventType.MARKET}
    
    def handle(self, event):
        if isinstance(event, MarketEvent):
            self.count += 1
            self.events_received.append({
                'symbol': event.symbol,
                'timestamp': event.timestamp,
                'has_data': event.data is not None
            })


def test_data_handler_to_registry_integration():
    """
    Test integración completa: CSV Data → MarketEvent → Registry → Handler
    """
    # Arrange: DataFrame con 3 barras de datos
    df = pd.DataFrame({
        'open': [100.0, 101.0, 102.0],
        'high': [105.0, 106.0, 107.0],
        'low': [99.0, 100.0, 101.0],
        'close': [104.0, 105.0, 106.0],
        'volume': [1000.0, 1100.0, 1200.0]
    }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))
    
    # Setup componentes
    events_queue = Queue()
    data_handler = HistoricCSVDataHandler(events_queue, "BTCUSDT", df)
    
    registry = EventHandlerRegistry()
    market_counter = SimpleMarketEventCounter()
    registry.register_handler(market_counter)
    
    # Act: Procesar todas las barras
    processed_events = 0
    while data_handler.continue_backtest and processed_events < 5:  # safety limit
        data_handler.update_bars()
        
        # Simular Event Bus: procesar eventos en la cola
        while not events_queue.empty():
            event = events_queue.get_nowait()
            if registry.has_handlers(event.type):
                handlers = registry.get_handlers(event.type)
                for handler in handlers:
                    handler.handle(event)
        
        processed_events += 1
    
    # Assert: Verificar integración completa
    assert market_counter.count == 3, f"Expected 3 events, got {market_counter.count}"
    assert len(market_counter.events_received) == 3
    
    # Verificar primer evento
    first_event = market_counter.events_received[0]
    assert first_event['symbol'] == "BTCUSDT"
    assert first_event['timestamp'] == pd.Timestamp('2023-01-01')
    assert first_event['has_data'] == True
    
    # Verificar que se procesaron todos los datos
    assert not data_handler.continue_backtest


def test_multiple_handlers_same_event():
    """
    Test que múltiples handlers reciben el mismo evento.
    """
    # Setup
    df = pd.DataFrame({
        'open': [100.0],
        'close': [105.0],
        'volume': [1000.0]
    }, index=[pd.Timestamp('2023-01-01')])
    
    events_queue = Queue()
    data_handler = HistoricCSVDataHandler(events_queue, "ETHUSD", df)
    
    registry = EventHandlerRegistry()
    counter1 = SimpleMarketEventCounter()
    counter2 = SimpleMarketEventCounter()
    
    registry.register_handler(counter1)
    registry.register_handler(counter2)
    
    # Act
    data_handler.update_bars()
    
    # Procesar evento con ambos handlers
    event = events_queue.get_nowait()
    handlers = registry.get_handlers(event.type)
    for handler in handlers:
        handler.handle(event)
    
    # Assert: Ambos handlers recibieron el evento
    assert counter1.count == 1
    assert counter2.count == 1
    assert counter1.events_received[0]['symbol'] == "ETHUSD"
    assert counter2.events_received[0]['symbol'] == "ETHUSD"
