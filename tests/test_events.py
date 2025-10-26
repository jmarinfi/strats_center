import pytest
from datetime import datetime
from models.events import BacktestEvent, ErrorEvent, Event, MarketEvent, PortfolioEvent, SignalEvent, OrderEvent, FillEvent
from models.enums import EventType, SignalType, OrderType, OrderDirection

def test_event_base():
    event = Event(type=EventType.MARKET)
    assert event.type == EventType.MARKET

def test_market_event_minimal_and_data_types():
    now = datetime.now()
    ev = MarketEvent(
        symbol="BTCUSDT",
        timestamp=now,
        data={
            "open": 50000.0,
            "close": 51000.0,
            "volume": 1_000_000.0,
            "datetime": now,  # Dict[str, Any] permite datetime
            "note": "bar-0",  # admite strings también
        },
    )
    assert ev.type == EventType.MARKET
    assert ev.symbol == "BTCUSDT"
    assert ev.timestamp == now
    assert isinstance(ev.data, dict)
    assert ev.data["open"] == 50000.0
    assert "datetime" in ev.data
    assert isinstance(ev.data["datetime"], datetime)

def test_market_event():
    event = MarketEvent(
        symbol="BTCUSDT",
        timestamp=datetime.now(),
        data={"open": 50000, "close": 51000}
    )
    assert event.type == EventType.MARKET

def test_signal_event():
    event = SignalEvent(type=EventType.SIGNAL, symbol="BTCUSDT", timestamp=datetime(2023,1,1), signal_type=SignalType.LONG)
    assert event.type == EventType.SIGNAL
    assert event.symbol == "BTCUSDT"
    assert event.signal_type == SignalType.LONG

def test_order_event():
    event = OrderEvent(type=EventType.ORDER, symbol="BTCUSDT", order_type=OrderType.LIMIT, quantity=1.5, direction=OrderDirection.BUY, timestamp=datetime.now())
    assert event.type == EventType.ORDER
    assert event.symbol == "BTCUSDT"
    assert event.order_type == OrderType.LIMIT
    assert event.quantity == 1.5
    assert event.direction == OrderDirection.BUY

def test_order_event_market_and_limit_timestamp_optional_price():
    now = datetime.now()
    # MARKET sin price
    ev_mkt = OrderEvent(
        type=EventType.ORDER,
        symbol="BTCUSDT",
        order_type=OrderType.MARKET,
        quantity=0.1,
        direction=OrderDirection.BUY,
        timestamp=now,
    )
    assert ev_mkt.type == EventType.ORDER
    assert ev_mkt.symbol == "BTCUSDT"
    assert ev_mkt.order_type == OrderType.MARKET
    assert ev_mkt.quantity == 0.1
    assert ev_mkt.direction == OrderDirection.BUY
    assert ev_mkt.timestamp == now
    assert ev_mkt.price is None  # opcional

    # LIMIT con price
    ev_lim = OrderEvent(
        type=EventType.ORDER,
        symbol="BTCUSDT",
        order_type=OrderType.LIMIT,
        quantity=0.2,
        direction=OrderDirection.SELL,
        timestamp=now,
        price=68000.0,
    )
    assert ev_lim.order_type == OrderType.LIMIT
    assert ev_lim.price == 68000.0

def test_fill_event():
    event = FillEvent(type=EventType.FILL, timestamp=datetime(2023,1,1), symbol="BTCUSDT", exchange="Binance", quantity=2.0, direction=OrderDirection.SELL, fill_cost=100.0, commission=0.1)
    assert event.type == EventType.FILL
    assert event.symbol == "BTCUSDT"
    assert event.exchange == "Binance"
    assert event.quantity == 2.0
    assert event.direction == OrderDirection.SELL
    assert event.fill_cost == 100.0
    assert event.commission == 0.1

def test_portfolio_event():
    now = datetime.now()
    ev = PortfolioEvent(
        type=EventType.PORTFOLIO,
        timestamp=now,
        total_value=10000.0,
        cash=5000.0,
        positions={"BTCUSDT": 0.1, "ETHUSD": 2.0},
    )
    assert ev.type == EventType.PORTFOLIO
    assert ev.timestamp == now
    assert ev.total_value == 10000.0
    assert ev.cash == 5000.0
    assert ev.positions["BTCUSDT"] == 0.1


def test_backtest_event():
    now = datetime.now()
    ev = BacktestEvent(
        type=EventType.BACKTEST,
        action="start",
        timestamp=now,
        message="Backtesting started",
    )
    assert ev.type == EventType.BACKTEST
    assert ev.action == "start"
    assert ev.timestamp == now
    assert ev.message == "Backtesting started"


def test_error_event():
    now = datetime.now()
    ev = ErrorEvent(
        type=EventType.ERROR,
        timestamp=now,
        source="strategy",
        error_type="ValidationError",
        message="Invalid parameter",
        details={"param": "period", "value": -1},
    )
    assert ev.type == EventType.ERROR
    assert ev.timestamp == now
    assert ev.source == "strategy"
    assert ev.error_type == "ValidationError"
    assert ev.message == "Invalid parameter"
    assert ev.details == {"param": "period", "value": -1}
