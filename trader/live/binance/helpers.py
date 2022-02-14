from binance.client import Client

from trader.core.exception import PositionError, SymbolError
from .position import BinancePosition
from .symbol_info import BinanceSymbolInfo


def get_symbol_info(client: Client, symbol: str):
    symbol = symbol.upper()

    for symbol_info in client.futures_exchange_info()["symbols"]:
        if symbol_info["symbol"] == symbol:
            return BinanceSymbolInfo(**symbol_info)

    raise SymbolError(f"No {symbol!r} symbol is found..")


def get_position(client: Client, symbol: str):
    symbol = symbol.upper()

    for position in client.futures_account()["positions"]:
        if position["symbol"] == symbol:
            return BinancePosition(position)

    raise PositionError(f"Position {symbol!r} is not found!")
