from __future__ import annotations

from binance.client import Client

import util.generate as generate
from trader.core.const import Market
from trader.live.binance import BinanceFuturesExchangeInfo, BinanceSpotExchangeInfo


def get_current_price(symbol: str, market: Market):
    if market is Market.FUTURES:
        return float(Client().futures_symbol_ticker(symbol=symbol)['price'])
    else:
        return float(Client().get_symbol_ticker(symbol=symbol)['price'])


def get_futures_symbol_info(symbol: str):
    return get_futures_exchange_info().get_symbol_info(symbol)


def get_spot_symbol_info(symbol: str):
    return get_spot_exchange_info().get_symbol_info(symbol)


def get_futures_exchange_info():
    return BinanceFuturesExchangeInfo(Client().futures_exchange_info())


def get_spot_exchange_info():
    return BinanceSpotExchangeInfo(Client().get_exchange_info())


def get_all_futures_symbol_info():
    return get_futures_exchange_info().symbols


def get_all_spot_symbol_info():
    return get_spot_exchange_info().symbols


def get_all_futures_base_asset():
    """
    Returns all unique base assets available on Binance Futures.

    :return: set of base assets
    """

    symbols = get_all_futures_symbol_info()
    return set(symbol.base_asset for symbol in symbols)


def get_all_futures_quote_asset():
    """
    Returns all unique quote assets available on Binance Futures.

    :return: set of quote assets
    """
    symbols = get_all_futures_symbol_info()
    return set(symbol.quote_asset for symbol in symbols)


def get_all_futures_symbol():
    """
    Returns all unique symbols available on Binance Futures.

    Symbol is a concatenation of a base and a quote asset (e.g.: 'BTC' + 'USDT' = 'BTCUSDT').

    :return: set of symbols
    """

    symbols = get_all_futures_symbol_info()
    return set(symbol.symbol for symbol in symbols)


def generate_client_order_id() -> str:
    length = 36

    _0_to_9 = ''.join(generate.char_sequence(48, 58))
    a_to_z = ''.join(generate.char_sequence(65, 91))
    A_to_Z = ''.join(generate.char_sequence(97, 123))

    return generate.random_string(r'.:/_-' + _0_to_9 + a_to_z + A_to_Z, length)
