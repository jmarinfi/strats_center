from abc import ABC, abstractmethod
import logging
from typing import Any, Callable, Dict, List

from models import OrderEvent
from models.config import ExchangeSettings
from models.exchange_state import Balance, Order, Ticker


MarketDataCallback = Callable[[Ticker], None]
OrderUpdateCallback = Callable[[Order], None]


class IExchangeConnector(ABC):
    """
    Interfaz abstracta para un conector de exchange.
    """

    def __init__(self, config: ExchangeSettings) -> None:
        self.config = config
        self._is_api_connected = False
        self._is_ws_connected = False
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Iniciando conector de exchange {self.__class__.__name__}")

    @abstractmethod
    def connect_api(self) -> None:
        """Establece y autentica la conexión con la API del exchange."""
        pass

    @abstractmethod
    def connect_ws(self) -> None:
        """Establece y autentica la conexión con el WebSocket del exchange."""
        pass

    @abstractmethod
    def disconnect_ws(self) -> None:
        """Cierra la conexión con el WebSocket del exchange."""
        pass

    # --- Métodos REST API ---

    @abstractmethod
    def fetch_balance(self) -> List[Balance]:
        """Obtiene el balance de la cuenta."""
        pass

    @abstractmethod
    def create_order(self, order: OrderEvent) -> Order:
        """Envía una nueva orden al exchange."""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str) -> Order:
        """Cancela una orden existente."""
        pass

    @abstractmethod
    def fetch_order_status(self, order_id: str, symbol: str) -> Order:
        """Consulta el estado de una orden existente."""
        pass

    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Ticker:
        """Obtiene el ticker actual de un símbolo."""
        pass

    # --- Métodos WebSocket ---

    @abstractmethod
    def subscribe_to_market_data(self, symbols: List[str], callback: MarketDataCallback) -> None:
        """Suscribe a un stream de datos de mercado para un símbolo."""
        pass

    @abstractmethod
    def subscribe_to_order_updates(self, callback: OrderUpdateCallback) -> None:
        """Suscribe a un stream de actualizaciones de órdenes."""
        pass

    # --- Propiedades de estado ---

    @property
    def is_api_connected(self) -> bool:
        """Indica si la conexión con la API del exchange está activa."""
        return self._is_api_connected
    
    @property
    def is_ws_connected(self) -> bool:
        """Indica si la conexión con el WebSocket del exchange está activa."""
        return self._is_ws_connected
