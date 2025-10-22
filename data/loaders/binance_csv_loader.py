from pathlib import Path
from typing import Dict, List

import pandas as pd

from data.loaders.i_data_loader import IDataLoader


class BinanceCSVLoader(IDataLoader):
    """
    Implementación de IDataLoader que carga archivos CSV con el formato
    estándar de Binance.
    """

    DATETIME_UNIT = "ms"
    
    def __init__(self, binance_columns: List[str] = [
        "openTime",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "closeTime",
        "quoteAssetVolume",
        "numberOfTrades"
    ]) -> None:
        super().__init__(binance_columns)

    def load(self, path: Path) -> pd.DataFrame:
        """Carga un archivo CSV de Binance, lo normaliza y lo devuelve."""
        try:
            df = pd.read_csv(path, header=0)
        except FileNotFoundError as e:
            print(f"Error: Archivo no encontrado en la ruta {path}: {e}")
            raise
        except Exception as e:
            print(f"Error al leer el archivo CSV {path}: {e}")
            raise

        # Renombrar las columnas según el mapeo definido
        try:
            df.rename(columns=self.mapping_columns, inplace=True)
        except Exception as e:
            print(f"Error al renombrar las columnas del DataFrame: {e}")
            raise

        # Convertir la columna de tiempo y establecerla como índice
        datetime_col = self.columns[0]
        if datetime_col not in df.columns:
            raise ValueError(f"La columna de tiempo original '{datetime_col}' no está en el DataFrame.")

        df[datetime_col] = pd.to_datetime(df[datetime_col], unit=self.DATETIME_UNIT)
        df.set_index(datetime_col, inplace=True)

        # Convertir las demás columnas a tipos numéricos
        for col in self.columns[1:]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            else:
                raise ValueError(f"La columna esperada '{col}' no está en el DataFrame.")
            
        # Eliminar filas con datos faltantes
        df.dropna(inplace=True)

        return df
