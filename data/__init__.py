"""
Data package for the trading platform.

This package contains data handlers and loaders for managing market data.
"""

# Data Handlers
from data.i_data_handler import IDataHandler
from data.historic_csv_data_handler import HistoricCSVDataHandler

# Data Loaders (from subpackage)
from data.loaders import (
    IDataLoader,
    BinanceCSVLoader,
)

__all__ = [
    # Data Handlers
    "IDataHandler",
    "HistoricCSVDataHandler",
    # Data Loaders
    "IDataLoader",
    "BinanceCSVLoader",
]
