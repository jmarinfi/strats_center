import logging
from queue import Queue, Empty

from models import TradingConfig, MarketEvent
from strategies import BaseStrategy
from data import IDataHandler
from event_bus import EventBus
from broker import IBroker
from portfolio import IPortfolio
from order_manager import IOrderManager


logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    Motor principal de backtesting.
    """

    def __init__(
            self,
            config: TradingConfig,
            data_handler: IDataHandler,
            strategy: BaseStrategy,
            portfolio: IPortfolio,
            order_manager: IOrderManager,
            broker: IBroker,
            event_bus: EventBus,
    ) -> None:
        self.config = config
        self.data_handler = data_handler
        self.strategy = strategy
        self.portfolio = portfolio
        self.order_manager = order_manager
        self.broker = broker
        self.event_bus = event_bus

        self.data_queue: Queue[MarketEvent] = self.data_handler.events_queue

        logger.info("BacktestEngine inicializado.")

    def run(self) -> None:
        """Ejectua el bucle principal de backtesting."""
        logger.info("Iniciando backtesting...")

        while self.data_handler.continue_backtest:

            # 1. El DataHandler genera un MarketEvent y lo pone en el data_queue
            self.data_handler.update_bars()

            # 2. El motor procesa la cola de datos
            while not self.data_queue.empty():
                try:
                    event = self.data_queue.get(block=False)
                except Empty:
                    break

                if event:
                    # 3. El motor publica el MarketEvent en el EventBus
                    logger.debug(f"Procesando MarketEvent para el símbolo {event.symbol} en {event.timestamp}")
                    self.event_bus.publish(event)

        logger.info("Backtesting finalizado.")

        self.portfolio.print_final_stats()
