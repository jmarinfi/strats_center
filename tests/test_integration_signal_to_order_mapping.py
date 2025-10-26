"""
Test de integración: Mapeo conceptual SignalEvent → OrderEvent
Este test codifica la lógica de negocio discutida sin implementar OrderManager aún.
"""

from datetime import datetime
from models.events import SignalEvent, OrderEvent
from models.enums import SignalType, OrderDirection, OrderType


def signal_to_order_direction(signal_type: SignalType, current_position: float) -> OrderDirection:
    """
    Función auxiliar que codifica el mapeo de señales a direcciones de orden.
    Esta lógica será implementada en el OrderManager futuro.
    
    Args:
        signal_type: Tipo de señal (LONG, SHORT, EXIT)
        current_position: Posición actual (+ = long, - = short, 0 = neutral)
    
    Returns:
        OrderDirection correspondiente
    """
    if signal_type == SignalType.LONG:
        return OrderDirection.BUY
    elif signal_type == SignalType.SHORT:
        return OrderDirection.SELL
    elif signal_type == SignalType.EXIT:
        if current_position > 0:  # Posición LONG
            return OrderDirection.SELL  # Vender para cerrar
        elif current_position < 0:  # Posición SHORT
            return OrderDirection.BUY   # Comprar para cerrar
        else:  # Sin posición
            raise ValueError("No position to exit")
    else:
        raise ValueError(f"Unknown signal type: {signal_type}")


def test_long_signal_to_buy_order():
    """Test: Señal LONG → BUY order"""
    now = datetime.now()
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.LONG
    )
    
    direction = signal_to_order_direction(signal.signal_type, current_position=0.0)
    assert direction == OrderDirection.BUY


def test_short_signal_to_sell_order():
    """Test: Señal SHORT → SELL order"""
    now = datetime.now()
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.SHORT
    )
    
    direction = signal_to_order_direction(signal.signal_type, current_position=0.0)
    assert direction == OrderDirection.SELL


def test_exit_long_position_to_sell():
    """Test: EXIT con posición LONG → SELL order"""
    now = datetime.now()
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.EXIT
    )
    
    direction = signal_to_order_direction(signal.signal_type, current_position=0.5)  # Long position
    assert direction == OrderDirection.SELL


def test_exit_short_position_to_buy():
    """Test: EXIT con posición SHORT → BUY order"""
    now = datetime.now()
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.EXIT
    )
    
    direction = signal_to_order_direction(signal.signal_type, current_position=-0.3)  # Short position
    assert direction == OrderDirection.BUY


def test_exit_no_position_raises_error():
    """Test: EXIT sin posición → Error"""
    now = datetime.now()
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.EXIT
    )
    
    try:
        signal_to_order_direction(signal.signal_type, current_position=0.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "No position to exit" in str(e)


def test_signal_to_order_event_creation():
    """
    Test integración: SignalEvent → conversión → OrderEvent
    Simula lo que haría un OrderManager futuro.
    """
    now = datetime.now()
    
    # Signal de entrada LONG
    signal = SignalEvent(
        symbol="BTCUSDT",
        timestamp=now,
        signal_type=SignalType.LONG
    )
    
    # Convertir a orden (simulando OrderManager)
    direction = signal_to_order_direction(signal.signal_type, current_position=0.0)
    
    order = OrderEvent(
        symbol=signal.symbol,
        timestamp=signal.timestamp,
        order_type=OrderType.MARKET,
        quantity=0.1,  # Cantidad fija para test
        direction=direction
    )
    
    # Verificar conversión correcta
    assert order.symbol == signal.symbol
    assert order.timestamp == signal.timestamp
    assert order.direction == OrderDirection.BUY
    assert order.order_type == OrderType.MARKET
    assert order.quantity == 0.1
