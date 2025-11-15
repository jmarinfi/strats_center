"""
Módulo para conectores de exchanges en vivo.

Este módulo proporciona las abstracciones y implementaciones 
para conectarse a exchanges de criptomonedas, tanto para 
obtener datos de mercado en vivo como para ejecutar órdenes.
"""
from .i_exchange_connector import (
    IExchangeConnector,
    MarketDataCallback,
    OrderUpdateCallback
)

__all__ = [
    "IExchangeConnector",
    "MarketDataCallback",
    "OrderUpdateCallback",
]