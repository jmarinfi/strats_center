from data.i_data_handler import IDataHandler


class HistoricCSVDataHandler(IDataHandler):
    """
    Manejador de datos que lee datos de mercado desde archivos CSV.
    """

    def __init__(self, ) -> None:
        super().__init__()