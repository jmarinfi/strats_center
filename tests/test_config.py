"""
Tests para la configuración del sistema de trading.
"""

import pytest
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


class TestConfigModels:
    """Tests para modelos individuales de configuración."""
    
    def test_symbol_config_defaults(self):
        """Test valores por defecto de SymbolConfig."""
        symbol = SymbolConfig(symbol="BTCUSDT")
        assert symbol.symbol == "BTCUSDT"
        assert symbol.enabled is True
        assert symbol.timeframe == "1h"
    
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
