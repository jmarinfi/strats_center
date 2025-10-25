import pytest
import pandas as pd
from pathlib import Path
from data.loaders.binance_csv_loader import BinanceCSVLoader
import tempfile

def test_binance_csv_loader(tmp_path):
    # Crear un archivo CSV temporal con formato Binance
    csv_content = """openTime,open,high,low,close,volume,closeTime,quoteAssetVolume,numberOfTrades
1672531200000,1,2,0,1.5,100,1672534800000,150,10
1672617600000,2,3,1,2.5,200,1672621200000,250,20
"""
    csv_file = tmp_path / "binance.csv"
    csv_file.write_text(csv_content)
    loader = BinanceCSVLoader()
    df = loader.load(csv_file)
    assert "open" in df.columns
    assert "close" in df.columns
    assert df.shape[0] == 2
    assert df.index[0] == pd.Timestamp("2023-01-01 00:00:00")
    assert df["open"].iloc[0] == 1
