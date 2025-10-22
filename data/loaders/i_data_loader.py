from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import pandas as pd


class IDataLoader(ABC):
    """
    Clase abstracta para cargadores de datos de mercado, tanto históricos como en vivo.
    """

    def __init__(self, exchange_columns: List[str]) -> None:
        self.columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades"
        ]
        self.mapping_columns = {
            exchange_col: standard_col
            for exchange_col, standard_col in zip(exchange_columns, self.columns)
        }
    
    @abstractmethod
    def load(self, path: Path) -> pd.DataFrame:
        """Carga datos desde la ruta especificada y los retorna como un DataFrame normalizado."""
        raise NotImplementedError("Este método debe ser implementado por la subclase.")