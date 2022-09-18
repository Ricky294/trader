from __future__ import annotations

import json
from typing import Callable, NoReturn, Any

import numpy as np
import websocket
from binance.exceptions import BinanceAPIException

import trader.log

from trader.core.const import Market

from trader.data.model import Candles
from trader.data.candle_schema import TOHLCV_LONG_TO_SHORT
from trader.live.binance.broker import localize_binance_exception

from util.func import any_func


BINANCE_SPOT_STREAM = 'wss://stream.binance.com:9443'
BINANCE_FUTURES_STREAM = 'wss://fstream.binance.com'


def candle_stream(
        candles: Candles,
        on_candle: Callable[[dict], Any],
        on_candle_close: Callable[[Candles], Any],
        on_exception: Callable[[websocket.WebSocketApp, Exception], Any] = any_func,
        log_candles=True,
) -> NoReturn:
    """
    Creates a candle stream on binance on symbol, interval and market defined by `candles` object instance attributes.

    :param candles: Historical candles.
    :param on_candle: Continuously called on new streaming data.
    :param on_candle_close: Calls this with the updated `candles` after a closed candle.
    :param log_candles: If True, new candles are continuously logged to console.
    """

    def message_callback(ws: websocket.WebSocketApp, raw_data):

        data = json.loads(raw_data)
        candle_data = data['k']

        candle_data['t'] /= 1000
        candle_data['T'] /= 1000
        candle_data['o'] = float(candle_data['o'])
        candle_data['h'] = float(candle_data['h'])
        candle_data['l'] = float(candle_data['l'])
        candle_data['c'] = float(candle_data['c'])
        candle_data['v'] = float(candle_data['v'])
        candle_data['q'] = float(candle_data['q'])
        candle_data['V'] = float(candle_data['V'])
        candle_data['Q'] = float(candle_data['Q'])

        if log_candles:
            trader.log.binance().info(candle_data)

        if candle_data['x']:
            new_candle = np.array([candle_data[TOHLCV_LONG_TO_SHORT[name]] for name in candles.schema], dtype=float)
            candles.concatenate(new_candle)
            on_candle_close(candles)

        on_candle(candle_data)

    def on_error(ws: websocket.WebSocketApp, exc: Exception):
        if isinstance(exc, BinanceAPIException):
            try:
                localize_binance_exception(exc)
            except Exception as e:
                exc = e

        trader.log.binance().critical(exc, exc_info=True)
        on_exception(ws, exc)
        trader.log.binance().info(f'Closing {ws.url} websocket because of the above error.')
        ws.close()

    def on_close(ws: websocket.WebSocketApp, close_status_code, close_msg):
        trader.log.binance().info(f'Connection closed: (status_code: {close_status_code}, message: {close_msg})')

    def on_open(ws: websocket.WebSocketApp):
        trader.log.binance().info(
            f'Starting {candles.symbol} candle stream '
            f'in {candles.interval} intervals on {candles.market} market.'
        )

    if candles.market is Market.FUTURES:
        stream = BINANCE_FUTURES_STREAM
    elif candles.market is Market.SPOT:
        stream = BINANCE_SPOT_STREAM
    else:
        raise ValueError(f'Invalid value for market: {candles.market}')

    url = f'{stream}/ws/{candles.symbol.pair.lower()}@kline_{candles.interval}'

    socket = websocket.WebSocketApp(
        url=url,
        on_open=on_open,
        on_message=message_callback,
        on_error=on_error,
        on_close=on_close,
    )
    socket.run_forever()
