from __future__ import annotations

import json
from typing import Callable, NoReturn

import numpy as np
import websocket

from trader.data.super_enum import Market
from trader.data.log import get_data_logger
from trader.data.model import Candles
from trader.data.candle_schema import TOHLCV_LONG_TO_SHORT

BINANCE_SPOT_STREAM = 'wss://stream.binance.com:9443'
BINANCE_FUTURES_STREAM = 'wss://fstream.binance.com'


def candle_stream(
        candles: Candles,
        on_candle: Callable[[dict], any],
        on_candle_close: Callable[[Candles, ...], any],
        on_candle_close_kwargs: Callable[[Candles], dict[str, any]],
        log_candles=True,
) -> NoReturn:
    """
    Creates a candle stream on binance on symbol, interval and market defined by `candles` object instance attributes.

    :param candles: Historical candles.
    :param on_candle_close_kwargs: Keyword arguments for on_candle_close function.
    :param on_candle_close: Calls this with the updated `candles` after a closed candle.
    :param on_candle: Continuously called on new streaming data.
    :param log_candles: If True, new candles are continuously logged to console.
    :return: Runs while stopped or crashed.
    """

    def message_callback(ws, raw_data):

        data = json.loads(raw_data)
        candle_data = data["k"]

        candle_data["t"] /= 1000
        candle_data["T"] /= 1000
        candle_data["o"] = float(candle_data["o"])
        candle_data["h"] = float(candle_data["h"])
        candle_data["l"] = float(candle_data["l"])
        candle_data["c"] = float(candle_data["c"])
        candle_data["v"] = float(candle_data["v"])
        candle_data["q"] = float(candle_data["q"])
        candle_data["V"] = float(candle_data["V"])
        candle_data["Q"] = float(candle_data["Q"])

        if log_candles:
            get_data_logger().info(candle_data)

        if candle_data["x"]:
            new_candle = np.array([candle_data[TOHLCV_LONG_TO_SHORT[name]] for name in candles.schema], dtype=float)
            candles.concatenate(new_candle)
            on_candle_close(**on_candle_close_kwargs(candles))

        on_candle(candle_data)

    def on_error(ws, error):
        get_data_logger().error(
            f"Connection closed with an error: ({error})"
        )

    def on_close(ws, close_status_code, close_msg):
        get_data_logger().info(
            f"Connection closed: (status_code: {close_status_code}, message: {close_msg})"
        )

    def on_open(ws):
        get_data_logger().info(
            f"Starting {candles.symbol} candle stream "
            f"in {candles.interval} intervals on binance {candles.market} market."
        )

    if candles.market == Market.FUTURES:
        stream = BINANCE_FUTURES_STREAM
    elif candles.market == Market.SPOT:
        stream = BINANCE_SPOT_STREAM
    else:
        raise ValueError(f"Invalid value for market: {candles.market}")

    url = f"{stream}/ws/{candles.symbol.lower()}@kline_{candles.interval}"
    socket = websocket.WebSocketApp(
        url=url,
        on_open=on_open,
        on_message=message_callback,
        on_error=on_error,
        on_close=on_close,
    )
    socket.run_forever()
