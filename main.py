import logging
import sys
from pathlib import Path
from queue import Queue

import pandas as pd

from backtest.engine import BacktestEngine
from backtest.simulated_broker import SimulatedBroker
from data import BinanceCSVLoader
from data.historic_csv_data_handler import HistoricCSVDataHandler
from event_bus import EventBus, EventHandlerRegistry
from models import TradingConfig, load_config
from models.config import DataSourceType
from order_manager.simple_order_manager import SimpleOrderManager
from portfolio import SimplePortfolio
from sizing import FixedQuantitySizer
from strategies.simple_price_strategy import SimplePriceStrategy


def setup_logging(config: TradingConfig) -> logging.Logger:
    """Configura el sistema de logging según la configuración cargada."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.logging.level, logging.INFO))

    while root_logger.handlers:
        handler = root_logger.handlers.pop()
        handler.close()

    formatter = logging.Formatter(config.logging.format)

    if config.logging.console.enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, config.logging.console.level, logging.INFO))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    if config.logging.file.enabled:
        log_path = Path(config.logging.file.path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(getattr(logging, config.logging.file.level, logging.INFO))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return logging.getLogger(__name__)


def load_historical_data(config: TradingConfig, logger: logging.Logger) -> pd.DataFrame:
    """Carga datos históricos para backtesting."""
    data_frames = []

    if config.data_source.type == DataSourceType.CSV:
        data_path = Path(config.data_source.csv.data_path)
        file_pattern = config.data_source.csv.file_pattern
        logger.info(f"Cargando datos CSV desde {data_path.absolute()} con patrón {file_pattern}")

        csv_files = list(data_path.glob(file_pattern))
        if not csv_files:
            raise FileNotFoundError("No se encontraron archivos CSV. Verifica la ruta y el patrón especificados.")
        
        logger.info(f"Se encontraron {len(csv_files)} archivos CSV para cargar.")
        
        loader = BinanceCSVLoader()

        for file in sorted(csv_files):
            try:
                df = loader.load(file)
                data_frames.append(df)
                logger.debug(f"Archivo {file.name} cargado con {df.shape[0]} filas.")
            except Exception as e:
                raise ValueError(f"Error al cargar el archivo {file.name}: {e}")
            
        if not data_frames:
            raise ValueError("No se pudieron cargar datos de los archivos CSV proporcionados.")
        
        all_data = pd.concat(data_frames)
        all_data.sort_index(inplace=True)
        all_data = all_data[~all_data.index.duplicated(keep='first')]

        logger.info(f"Datos concatenados y ordenados. Total de filas {len(all_data)}. Período desde {all_data.index.min()} hasta {all_data.index.max()}.")

        return all_data
    
    else:
        raise NotImplementedError(f"Tipo de fuente de datos {config.data_source.type} no soportado para carga histórica.")


def main():

    # Cargar configuración

    config = load_config()
    logger = setup_logging(config)

    logger.info("Configuración de la aplicación: %s", config.app)
    logger.info("Configuración de la fuente de datos: %s", config.data_source)
    logger.info("Configuración de la estrategia: %s", config.strategy)
    logger.info("Configuración de backtesting: %s", config.backtesting)
    logger.info("Configuración de la base de datos: %s", config.database)
    logger.info("Configuración del sistema de eventos: %s", config.events)
    logger.info("Configuración del sistema de logging: %s", config.logging)
    logger.info("Configuración de los símbolos: %s", config.symbols)

    logger.info("Aplicación iniciada")

    if config.app.debug:
        logger.debug("Modo de depuración activado")

    # Inicializar el registro y el bus de eventos

    registry = EventHandlerRegistry()
    event_bus = EventBus(
        registry=registry,
        max_history=config.events.max_event_history,
    )
    logger.info(
        "Event Bus inicializado con historial máximo de %d eventos",
        config.events.max_event_history,
    )

    # Instanciar y registrar componentes del sistema

    historical_data = load_historical_data(config, logger)
    symbol = config.symbols[0].symbol
    data_handler = HistoricCSVDataHandler(
        events_queue=Queue(),
        symbol=symbol,
        data_frame=historical_data
    )
    logger.info(
        "HistoricCSVDataHandler instanciado para el símbolo %s con %d filas de datos",
        symbol,
        historical_data.shape[0],
    )

    strategy = SimplePriceStrategy(
        name="SimplePriceStrategy",
        symbols=[symbol],
        event_bus=event_bus
    )
    registry.register_handler(strategy)
    logger.info("SimplePriceStrategy registrada en el Event Bus")

    portfolio = SimplePortfolio(
        event_bus=event_bus,
        data_handler=data_handler,
        initial_capital=config.backtesting.initial_capital
    )
    registry.register_handler(portfolio)
    logger.info(f"SimplePortfolio registrada en el Event Bus con capital inicial {config.backtesting.initial_capital}")

    sizer = FixedQuantitySizer(
        default_quantity=config.strategy.sizing.value
    )
    logger.info(
        "FixedQuantitySizer instanciado con cantidad por defecto %f",
        config.strategy.sizing.value
    )

    order_manager = SimpleOrderManager(
        event_bus=event_bus,
        portfolio=portfolio,
        data_handler=data_handler,
        sizer=sizer
    )
    registry.register_handler(order_manager)
    logger.info(f"SimpleOrderManager registrada en el Event Bus.")

    broker = SimulatedBroker(
        event_bus=event_bus,
        commission_config=config.backtesting.commission,
        data_handler=data_handler
    )
    registry.register_handler(broker)
    logger.info("SimulatedBroker registrada en el Event Bus.")

    # Inicializar y ejecutar el motor de backtesting

    engine = BacktestEngine(
        config=config,
        data_handler=data_handler,
        strategy=strategy,
        portfolio=portfolio,
        order_manager=order_manager,
        broker=broker,
        event_bus=event_bus
    )
    
    engine.run()

if __name__ == "__main__":
    main()
