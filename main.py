import os
from pathlib import Path

from data import BinanceCSVLoader


def main():
    loader = BinanceCSVLoader()
    for filename in os.listdir("backtest_data"):
        print(f"Cargando archivo: {filename}")
        path_data = Path("backtest_data") / filename
        df = loader.load(path_data)
        print(f"Datos cargados desde {filename}:")
        print(df.head())


if __name__ == "__main__":
    main()
