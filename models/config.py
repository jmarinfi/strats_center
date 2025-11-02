"""
Módulo para definir la configuración del sistema de trading.
"""

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource


class DataSourceType(str, Enum):
    """
    Enum que define los tipos de fuentes de datos soportadas.
    """
    CSV = "csv"
    BINANCE_API = "binance_api"
    PAPER_TRADING = "paper_trading"


class LogLevel(str, Enum):
    """
    Enum que define los niveles de log soportados.
    """
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class CommissionType(str, Enum):
    """
    Enum que define los tipos de comisiones soportadas.
    """
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class SizingType(str, Enum):
    """
    Enum que define los tipos de dimensionamiento de órdenes soportados.
    """
    FIXED = "fixed"
    PERCENTAGE = "percentage"


class EventBusType(str, Enum):
    """
    Enum que define los tipos de buses de eventos soportados.
    """
    IN_MEMORY = "in_memory"
    REDIS = "redis"


class DatabaseType(str, Enum):
    """
    Enum que define los tipos de bases de datos soportadas.
    """
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


# Modelos de configuración
class AppConfig(BaseModel):
    """
    Modelo de configuración principal de la aplicación.
    """
    name: str = "StratsCenter"
    version: str = "0.1.0"
    debug: bool = True
    log_level: LogLevel = LogLevel.INFO


class CSVDataSourceSettings(BaseModel):
    """
    Modelo de configuración para una fuente de datos CSV.
    """
    data_path: str = "backtest_data"
    file_pattern: str = "*.csv"
    timestamp_column: str = "openTime"


class BinanceAPISettings(BaseModel):
    """
    Modelo de configuración para la API de Binance.
    """
    api_key: str = ""
    api_secret: str = ""
    base_url: str = "https://api.binance.com"


class DataSourceConfig(BaseModel):
    """
    Modelo de configuración para la fuente de datos.
    """
    type: DataSourceType = DataSourceType.CSV
    csv: CSVDataSourceSettings = Field(default_factory=lambda: CSVDataSourceSettings())
    binance_api: BinanceAPISettings = Field(default_factory=lambda: BinanceAPISettings())


class RiskManagementConfig(BaseModel):
    """
    Modelo de configuración para la gestión de riesgos.
    """
    max_position_size: float = Field(default=1.0, ge=0.0, le=1.0, description="Tamaño máximo de posición como fracción del capital total.")
    stop_loss_pct: Optional[float] = Field(default=5.0, ge=0.0, le=100.0, description="Porcentaje de stop loss.")
    take_profit_pct: Optional[float] = Field(default=15.0, ge=0.0, description="Porcentaje de take profit.")


class SizingConfig(BaseModel):
    """
    Modelo de configuración para el dimensionamiento de órdenes.
    """
    type: SizingType = SizingType.FIXED
    value: float = Field(default=0.1, gt=0.0, description="Valor de dimensionamiento. Si es 'fixed', es la cantidad fija; si es 'percentage', es el porcentaje del capital total.")


class StrategyConfig(BaseModel):
    """
    Modelo de configuración para una estrategia de trading.
    """
    name: str
    enabled: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    risk_management: RiskManagementConfig = Field(default_factory=lambda: RiskManagementConfig())
    sizing: SizingConfig = Field(default_factory=lambda: SizingConfig())

    @model_validator(mode="after")
    def validate_strategy_parameters(self) -> "StrategyConfig":
        """Valida los parámetros específicos de la estrategia."""
        if self.name == "sma_crossover":
            required_params = ["short_period", "long_period"]
            for param in required_params:
                if param not in self.parameters:
                    raise ValueError(f"El parámetro '{param}' es obligatorio para la estrategia SMA Crossover.")
                
            short_period = self.parameters.get("short_period", 0)
            long_period = self.parameters.get("long_period", 0)

            if short_period >= long_period:
                raise ValueError("El 'short_period' debe ser menor que el 'long_period'.")
            
        return self
    

class CommissionConfig(BaseModel):
    """
    Modelo de configuración para las comisiones de trading.
    """
    type: CommissionType = CommissionType.PERCENTAGE
    rate: float = Field(default=0.001, ge=0.0, description="Tasa de comisión (por ejemplo, 0.001 para 0.1%).")


class BacktestingConfig(BaseModel):
    """
    Modelo de configuración para backtesting.
    """
    enabled: bool = True
    initial_capital: float = Field(default=10000.0, gt=0.0, description="Capital inicial para backtesting.")
    commission: CommissionConfig = Field(default_factory=lambda: CommissionConfig())
    start_date: Optional[str] = Field(default=None, description="Fecha de inicio del backtest (YYYY-MM-DD) o nulo para utilizar todos los datos.")
    end_date: Optional[str] = Field(default=None, description="Fecha de fin del backtest (YYYY-MM-DD) o nulo para utilizar todos los datos.")
    save_trades: bool = True
    save_portfolio_snapshots: bool = True
    generate_report: bool = True


class SQLiteSettings(BaseModel):
    """
    Modelo de configuración para SQLite.
    """
    path: str = "data/strats_center.db"
    pool_size: int = 5
    max_overflow: int = 10

    @field_validator('path')
    @classmethod
    def create_db_directory(cls, v: str) -> str:
        """Crea el directorio para la base de datos si no existe."""
        db_path = Path(v)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return v
    

class DatabaseConfig(BaseModel):
    """
    Modelo de configuración para la base de datos.
    """
    type: DatabaseType = DatabaseType.SQLITE
    sqlite: SQLiteSettings = Field(default_factory=lambda: SQLiteSettings())


class EventsConfig(BaseModel):
    """
    Modelo de configuración para el sistema de eventos.
    """
    event_bus_type: EventBusType = EventBusType.IN_MEMORY
    max_event_history: int = Field(default=10000, gt=0)
    enable_event_persistence: bool = True


class ConsoleLogHandler(BaseModel):
    """
    Modelo de configuración para el manejador de logs en consola.
    """
    enabled: bool = True
    level: LogLevel = LogLevel.INFO


class FileLogHandler(BaseModel):
    """
    Modelo de configuración para el manejador de logs en archivo.
    """
    enabled: bool = True
    level: LogLevel = LogLevel.DEBUG
    path: str = "logs/strats_center.log"
    max_size_mb: int = 10
    backup_count: int = 5

    @field_validator('path')
    @classmethod
    def create_log_directory(cls, v: str) -> str:
        """Crea el directorio para los logs si no existe."""
        log_path = Path(v)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return v
    

class LoggingConfig(BaseModel):
    """
    Modelo de configuración para el sistema de logging.
    """
    level: LogLevel = LogLevel.INFO
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    console: ConsoleLogHandler = Field(default_factory=lambda: ConsoleLogHandler())
    file: FileLogHandler = Field(default_factory=lambda: FileLogHandler())


class SymbolConfig(BaseModel):
    """
    Modelo de configuración para un símbolo financiero.
    """
    symbol: str = Field(..., min_length=1, description="Símbolo financiero, por ejemplo 'BTCUSDT'.")
    enabled: bool = True
    timeframe: str = Field(default="1h", description="Intervalo de tiempo para los datos, por ejemplo '1m', '5m', '1h', '1d'.")

    @field_validator('symbol')
    @classmethod
    def validate_symbol_format(cls, v: str) -> str:
        """Valida el formato del símbolo financiero."""
        if not v.replace("/", "").isalnum():
            raise ValueError("El símbolo financiero debe ser alfanumérico y puede incluir '/'.")
        return v.upper()
    

class TradingConfig(BaseSettings):
    """
    Modelo de configuración principal para el sistema de trading.
    """

    # Secciones de configuración
    app: AppConfig = Field(default_factory=lambda: AppConfig())
    data_source: DataSourceConfig = Field(default_factory=lambda: DataSourceConfig())
    strategy: StrategyConfig = Field(..., description="Configuración de la estrategia de trading.")
    backtesting: BacktestingConfig = Field(default_factory=lambda: BacktestingConfig()) # type: ignore
    database: DatabaseConfig = Field(default_factory=lambda: DatabaseConfig())
    events: EventsConfig = Field(default_factory=lambda: EventsConfig()) # type: ignore
    logging: LoggingConfig = Field(default_factory=lambda: LoggingConfig())
    symbols: List[SymbolConfig] = Field(default_factory=list)

    # Configuraciones de pydantic-settings
    model_config = SettingsConfigDict(
        yaml_file="config/strategy_config.yaml",
        yaml_file_encoding="utf-8",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="forbid"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type["BaseSettings"],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings
    ):
        """Personaliza las fuentes de configuración para incluir archivos YAML."""
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings
        )

    @model_validator(mode="after")
    def validate_symbols_not_empty(self) -> "TradingConfig":
        """Valida que la lista de símbolos no esté vacía."""
        symbols = self.symbols
        if not symbols:
            self.symbols = [SymbolConfig(symbol="BTCUSDT")]
        return self


def load_config() -> TradingConfig:
    """
    Carga la configuración desde un archivo YAML.
    """
    return TradingConfig() # type: ignore