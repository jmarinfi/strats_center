import os
from queue import Queue
from typing import Any, Dict, Iterator, List, Optional, Tuple

from pandas import DataFrame, Series
import pandas as pd
from data.i_data_handler import IDataHandler
from models.events import MarketEvent


class HistoricCSVDataHandler(IDataHandler):
    """
    HistoricCSVDataHandler está diseñado para leer archivos CSV para
    cada símbolo solicitado desde el disco y proporcionar barras, una
    a la vez, al sistema de backtesting.
    """

    def __init__(
            self,
            events_queue: Queue[MarketEvent],
            symbol: str,
            data_frame: DataFrame
    ) -> None:
        self.events_queue = events_queue
        self.symbol = symbol

        self.latest_symbol_data: List[Series] = []
        self._continue_backtest = True
        self._bar_iterator: Iterator[Tuple[Any, Series]] = data_frame.iterrows()

    @property
    def continue_backtest(self) -> bool:
        """Indica si el backtesting debe continuar."""
        return self._continue_backtest
        
    def _get_new_bar(self) -> Optional[Tuple[Any, Series]]:
        """Devuelve la última barra del feed de datos como una tupla (timestamp, Series)."""
        try:
            return next(self._bar_iterator)
        except StopIteration:
            self._continue_backtest = False
            return None
        except Exception as e:
            print(f"Error al obtener una nueva barra para el símbolo {self.symbol}: {e}")
            self._continue_backtest = False
            return None
        
    def update_bars(self) -> None:
        """Obtiene la siguiente barra de datos y, si tiene éxito, la almacena y coloca un MarketEvent en la cola de eventos."""
        if not self.continue_backtest:
            return
        
        bar_tuple = self._get_new_bar()

        if bar_tuple is not None:
            index, bar_data = bar_tuple

            bar_data_with_dt = bar_data.copy()
            bar_data_with_dt['datetime'] = index

            self.latest_symbol_data.append(bar_data_with_dt)

            self.events_queue.put(MarketEvent(
                symbol=self.symbol,
                timestamp=index,
                data=bar_data_with_dt.to_dict()
            ))

    def get_latest_bars(self, N: int = 1) -> List[Series]:
        """Devuelve las últimas N barras."""
        try:
            return self.latest_symbol_data[-N:]
        except Exception as e:
            # No hay suficientes barras disponibles, devolver todas las disponibles
            return self.latest_symbol_data

