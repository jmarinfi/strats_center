import pytest
import pandas as pd
from queue import Queue
from models.events import MarketEvent
from data.historic_csv_data_handler import HistoricCSVDataHandler

def test_historic_csv_data_handler_basic():
    # Crear un DataFrame de ejemplo
    df = pd.DataFrame({
        'open': [1,2],
        'high': [2,3],
        'low': [0,1],
        'close': [1.5,2.5],
        'volume': [100,200],
        'datetime': [pd.Timestamp('2023-01-01'), pd.Timestamp('2023-01-02')]
    })
    df.set_index('datetime', inplace=True)
    queue = Queue()
    handler = HistoricCSVDataHandler(queue, symbol="BTCUSDT", data_frame=df)
    assert handler.symbol == "BTCUSDT"
    assert handler.continue_backtest is True
    handler.update_bars()
    assert len(handler.latest_symbol_data) == 1
    assert not queue.empty()
    event = queue.get()
    assert isinstance(event, MarketEvent)
    handler.update_bars()
    assert len(handler.latest_symbol_data) == 2
    handler.update_bars()
    assert handler.continue_backtest is False
    bars = handler.get_latest_bars(2)
    assert len(bars) == 2
