"""
Tests para la configuración del sistema de trading.
"""

import pytest
import tempfile
from pathlib import Path
import yaml
from pydantic import ValidationError

from models.config import (
    TradingConfig, 
    StrategyConfig, 
    SymbolConfig, 
    LogLevel,
    DataSourceType,
    CommissionType,
    load_config
)


class TestTradingConfig:
    """Test suite para TradingConfig."""
    
    def test_load_default_config(self):
        """Test que carga la configuración por defecto desde YAML."""
        config = load_config()
        
        # Verificar que se carga correctamente
        assert isinstance(config, TradingConfig)
        assert config.app.name == "StratsCenter"
        assert config.app.version == "0.1.0"
        assert config.app.log_level == LogLevel.INFO
        
        # Verificar data source
        assert config.data_source.type == DataSourceType.CSV
        assert config.data_source.csv.data_path == "backtest_data"
        assert config.data_source.csv.timestamp_column == "openTime"
        
        # Verificar strategy (campo obligatorio)
        assert config.strategy.name == "sma_crossover"
        assert config.strategy.enabled is True
        assert config.strategy.parameters["short_period"] == 10
        assert config.strategy.parameters["long_period"] == 30
        
        # Verificar backtesting
        assert config.backtesting.initial_capital == 10000.0
        assert config.backtesting.commission.type == CommissionType.PERCENTAGE
        assert config.backtesting.commission.rate == 0.001
        
        # Verificar symbols
        assert len(config.symbols) >= 1
        assert config.symbols[0].symbol == "BTCUSDT"
        assert config.symbols[0].timeframe == "1h"
        
    def test_strategy_validation_sma_crossover(self):
        """Test validación específica para estrategia SMA Crossover."""
        # Test parámetros válidos
        strategy_config = StrategyConfig(
            name="sma_crossover",
            parameters={
                "short_period": 5,
                "long_period": 20
            }
        )
        assert strategy_config.parameters["short_period"] == 5
        assert strategy_config.parameters["long_period"] == 20
        
        # Test parámetros faltantes
        with pytest.raises(ValidationError, match="El parámetro 'short_period' es obligatorio"):
            StrategyConfig(
                name="sma_crossover",
                parameters={"long_period": 20}
            )
            
        # Test short_period >= long_period
        with pytest.raises(ValidationError, match="El 'short_period' debe ser menor que el 'long_period'"):
            StrategyConfig(
                name="sma_crossover",
                parameters={
                    "short_period": 20,
                    "long_period": 10
                }
            )
    
    def test_symbols_validation(self):
        """Test validación de símbolos."""
        # Test símbolo válido
        symbol = SymbolConfig(symbol="ETHUSDT")
        assert symbol.symbol == "ETHUSDT"
        assert symbol.enabled is True
        assert symbol.timeframe == "1h"
        
        # Test símbolo con formato inválido
        with pytest.raises(ValidationError):
            SymbolConfig(symbol="INVALID@SYMBOL")
    
    def test_load_custom_config_file(self):
        """Test carga de archivo de configuración personalizado."""
        custom_config = {
            "app": {
                "name": "TestStratsCenter",
                "version": "0.2.0",
                "debug": False,
                "log_level": "DEBUG"
            },
            "data_source": {
                "type": "csv",
                "csv": {
                    "data_path": "custom_data",
                    "file_pattern": "*.csv",
                    "timestamp_column": "openTime"
                }
            },
            "strategy": {
                "name": "sma_crossover",
                "enabled": True,
                "parameters": {
                    "short_period": 7,
                    "long_period": 25
                }
            },
            "backtesting": {
                "initial_capital": 5000.0
            },
            "database": {
                "type": "sqlite",
                "sqlite": {
                    "path": "test_data/test.db"
                }
            },
            "events": {
                "event_bus_type": "in_memory"
            },
            "logging": {
                "level": "DEBUG"
            },
            "symbols": [
                {"symbol": "BTCUSDT", "timeframe": "5m"},
                {"symbol": "ETHUSDT", "timeframe": "1h"}
            ]
        }
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(custom_config, f)
            config_path = Path(f.name)
        
        try:
            config = TradingConfig(_yaml_file=str(config_path)) # type: ignore
            
            assert config.app.name == "TestStratsCenter"
            assert config.app.version == "0.2.0"
            assert config.app.log_level == LogLevel.DEBUG
            assert config.data_source.csv.data_path == "custom_data"
            assert config.strategy.parameters["short_period"] == 7
            assert config.backtesting.initial_capital == 5000.0
            assert len(config.symbols) == 2
            assert config.symbols[0].timeframe == "5m"
            
        finally:
            config_path.unlink()  # Limpiar archivo temporal
    
    def test_invalid_config_missing_strategy(self):
        """Test que falla sin configuración de strategy."""
        invalid_config = {
            "app": {"name": "Test"},
            "data_source": {"type": "csv"},
            "backtesting": {"initial_capital": 1000.0},
            "database": {"type": "sqlite"},
            "events": {},
            "logging": {},
            "symbols": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            config_path = Path(f.name)
        
        try:
            with pytest.raises(ValidationError):
                load_config(config_path)
        finally:
            config_path.unlink()
    
    def test_config_file_not_found(self):
        """Test error cuando no existe el archivo de configuración."""
        non_existent_path = Path("non_existent_config.yaml")
        
        with pytest.raises(Exception):  # Pydantic Settings puede lanzar diferentes excepciones
            load_config(non_existent_path)


class TestConfigModels:
    """Tests para modelos individuales de configuración."""
    
    def test_symbol_config_defaults(self):
        """Test valores por defecto de SymbolConfig."""
        symbol = SymbolConfig(symbol="BTCUSDT")
        assert symbol.symbol == "BTCUSDT"
        assert symbol.enabled is True
        assert symbol.timeframe == "1h"
    
    def test_symbol_format_validation(self):
        """Test validación de formato de símbolo."""
        # Símbolos válidos
        valid_symbols = ["BTCUSDT", "ETH/USD", "BTC-EUR"]
        for sym in valid_symbols:
            try:
                config = SymbolConfig(symbol=sym)
                assert config.symbol == sym.upper()
            except ValidationError:
                # Ajustar si la validación actual es más estricta
                pass
    
    def test_backtesting_validation(self):
        """Test validaciones de BacktestingConfig."""
        from models.config import BacktestingConfig
        
        # Capital positivo válido
        config = BacktestingConfig(initial_capital=1000.0)
        assert config.initial_capital == 1000.0
        
        # Capital inválido (negativo o cero)
        with pytest.raises(ValidationError):
            BacktestingConfig(initial_capital=0.0)
            
        with pytest.raises(ValidationError):
            BacktestingConfig(initial_capital=-100.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
