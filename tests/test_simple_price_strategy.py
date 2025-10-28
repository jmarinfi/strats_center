# tests/test_simple_price_strategy.py

import pytest
from datetime import datetime
from unittest.mock import Mock

from strategies.simple_price_strategy import SimplePriceStrategy
from models import MarketEvent, SignalType, SignalEvent

@pytest.fixture
def mock_event_bus():
    """Crea un mock del EventBus."""
    return Mock()

@pytest.fixture
def strategy(mock_event_bus):
    """Crea una instancia de la estrategia para los tests."""
    symbols = ["BTCUSDT"]
    return SimplePriceStrategy(name="TestSimplePrice", symbols=symbols, event_bus=mock_event_bus)

def test_calculate_signal_long(strategy):
    """Verifica que se genera señal LONG cuando C > O."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'open': 100.0, 'high': 110.0, 'low': 95.0, 'close': 105.0, 'volume': 1000}
    )
    signal = strategy.calculate_signal(market_event)
    assert signal == SignalType.LONG

def test_calculate_signal_exit_when_close_less_than_open(strategy):
    """Verifica que se genera señal EXIT cuando C < O."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'open': 100.0, 'high': 105.0, 'low': 90.0, 'close': 95.0, 'volume': 1000}
    )
    signal = strategy.calculate_signal(market_event)
    assert signal == SignalType.EXIT

def test_calculate_no_signal_when_close_equals_open(strategy):
    """Verifica que no se genera señal cuando C == O."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'open': 100.0, 'high': 105.0, 'low': 95.0, 'close': 100.0, 'volume': 1000}
    )
    signal = strategy.calculate_signal(market_event)
    assert signal == None

def test_calculate_signal_no_data(strategy):
    """Verifica que no se genera señal si no hay datos."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data=None # Sin datos
    )
    signal = strategy.calculate_signal(market_event)
    assert signal is None

def test_calculate_signal_missing_prices(strategy):
    """Verifica que no se genera señal si faltan precios O o C."""
    now = datetime.now()
    market_event_no_close = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'open': 100.0} # Falta close
    )
    signal = strategy.calculate_signal(market_event_no_close)
    assert signal is None

    market_event_no_open = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'close': 100.0} # Falta open
    )
    signal = strategy.calculate_signal(market_event_no_open)
    assert signal is None

def test_handle_market_event_emits_signal(strategy, mock_event_bus):
    """Verifica que handle llama a _emit_signal (y este a event_bus.publish)."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={'open': 100.0, 'close': 105.0} # C > O -> LONG
    )

    # Llamar al handler principal
    strategy.handle(market_event)

    # Verificar que se llamó a publish en el event bus
    mock_event_bus.publish.assert_called_once()
    # Verificar el argumento con el que se llamó
    call_args = mock_event_bus.publish.call_args
    published_event = call_args[0][0] # El primer argumento posicional de la llamada

    assert isinstance(published_event, SignalEvent)
    assert published_event.symbol == "BTCUSDT"
    assert published_event.timestamp == now
    assert published_event.signal_type == SignalType.LONG

def test_handle_market_event_wrong_symbol(strategy, mock_event_bus):
    """Verifica que la estrategia ignora eventos de símbolos no suscritos."""
    now = datetime.now()
    market_event = MarketEvent(
        symbol="ETHUSDT", # Símbolo diferente al suscrito ("BTCUSDT")
        timestamp=now,
        data={'open': 2000.0, 'close': 2100.0}
    )

    strategy.handle(market_event)

    # Verificar que NO se llamó a publish
    mock_event_bus.publish.assert_not_called()