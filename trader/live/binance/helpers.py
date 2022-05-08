from binance.client import Client

from trader.core.util.common import generate_character_sequence, generate_random_string
from trader.core.exception import PositionError, SymbolError
from .position import BinancePosition
from .symbol_info import BinanceSymbolInfo


def get_symbol_info(client: Client, symbol: str):
    symbol = symbol.upper()

    for symbol_info in client.futures_exchange_info()["symbols"]:
        if symbol_info["symbol"] == symbol:
            return BinanceSymbolInfo(**symbol_info)

    raise SymbolError(symbol)


def get_position(client: Client, symbol: str):
    symbol = symbol.upper()

    for position in client.futures_account()["positions"]:
        if position["symbol"] == symbol:
            try:
                return BinancePosition(position)
            except PositionError:
                return None

    raise PositionError(f"Position {symbol!r} not found!")


def generate_client_order_id() -> str:
    length = 36

    zero_to_nine = "".join(generate_character_sequence(48, 58))
    a_to_z = "".join(generate_character_sequence(65, 91))
    A_to_Z = "".join(generate_character_sequence(97, 123))

    return generate_random_string(r".:/_-" + zero_to_nine + a_to_z + A_to_Z, length)
