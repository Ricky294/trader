from __future__ import annotations

from binance.client import Client

from trader.data.enumerate import Market
from trader.core.util.common import generate_character_sequence, generate_random_string
from trader.core.exception import PositionError, SymbolError, MarketError
from trader.live.binance.position import BinancePosition
from trader.live.binance.symbol_info import BinanceFuturesSymbolInfo


def get_symbol_info(symbol: str, market: str | Market):
    for symbol_info in get_all_symbol_info(market):
        if symbol_info.symbol == symbol:
            return symbol_info

    raise SymbolError(symbol)


def get_exchange_info(market: str | Market):
    market = str(market).upper()
    if market == 'FUTURES':
        return Client().futures_exchange_info()
    elif market == 'SPOT':
        return Client().get_exchange_info()
    raise MarketError(market)


def get_all_symbol_info(market: str | Market):
    return get_exchange_info(market)['symbol']


def get_all_base_asset(market: str | Market):
    """
    Returns all unique base assets available on Binance `market`.

    :param market: 'FUTURES' or 'SPOT'
    :return: set of base assets
    """

    symbols = get_all_symbol_info(market)
    return set(symbol['baseAsset'] for symbol in symbols)


def get_all_quote_asset(market: str | Market):
    """
    Returns all unique quote assets available on Binance `market`.

    :param market: 'FUTURES' or 'SPOT'
    :return: set of quote assets
    """
    symbols = get_all_symbol_info(market)
    return set(symbol['quoteAsset'] for symbol in symbols)


def get_all_symbol(market: str | Market):
    """
    Returns all unique symbols available on Binance `market`.

    Symbol is a concatenation of a base asset and a quote asset (e.g.: 'BTC' + 'USDT' = 'BTCUSDT').

    :param market: 'FUTURES' or 'SPOT'
    :return: set of symbols
    """

    symbols = get_all_symbol_info(market)
    return set(symbol['symbol'] for symbol in symbols)


def get_position(client: Client, symbol: str):
    symbol = symbol.upper()

    for position in client.futures_account()['positions']:
        if position['symbol'] == symbol:
            try:
                return BinancePosition(position)
            except PositionError:
                return None

    raise PositionError(f'Position {symbol!r} not found!')


def generate_client_order_id() -> str:
    length = 36

    zero_to_nine = ''.join(generate_character_sequence(48, 58))
    a_to_z = ''.join(generate_character_sequence(65, 91))
    A_to_Z = ''.join(generate_character_sequence(97, 123))

    return generate_random_string(r'.:/_-' + zero_to_nine + a_to_z + A_to_Z, length)
