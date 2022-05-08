from __future__ import annotations

import json
from typing import Callable

import numpy as np
import websocket

from trader.data.log import TRADER_DATA_LOGGER
from trader.data.model import Candles
from trader.data.schema import NAME_TO_SHORT_NAME

BINANCE_SPOT_STREAM = 'wss://stream.binance.com:9443'
BINANCE_FUTURES_STREAM = 'wss://fstream.binance.com'


def candle_stream(
        candles: Candles,
        on_candle_close: Callable[[Candles], any],
        on_candle: Callable[[dict], any],
        log_candles=True,
) -> None:
    """
    Creates a candle stream on binance on symbol, interval and market defined by `candles` object instance attributes.

    :param candles: Candles object to append data when a candle is closed.
    :param on_candle_close: Calls this with the updated `candles` after a closed candle.
    :param on_candle: Continuously called on new streaming data.
    :param log_candles: If True, new candles are continuously logged to console.
    :return: None
    """

    def message_callback(ws, raw_data):
        nonlocal candles

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
            TRADER_DATA_LOGGER.info(candle_data)

        if candle_data["x"]:
            new_candle = np.array([candle_data[NAME_TO_SHORT_NAME[name]] for name in candles.schema], dtype=float)
            candles.concatenate(new_candle)
            on_candle_close(candles)

        on_candle(candle_data)

    def on_error(ws, error):
        TRADER_DATA_LOGGER.error(
            f"Connection closed with an error: ({error})"
        )

    def on_close(ws, close_status_code, close_msg):
        TRADER_DATA_LOGGER.info(
            f"Connection closed: (status_code: {close_status_code}, message: {close_msg})"
        )

    def on_open(ws):
        TRADER_DATA_LOGGER.info(
            f"Starting {candles.symbol} candle stream "
            f"in {candles.interval} intervals on binance {candles.market} market."
        )

    if str(candles.market).upper() == "FUTURES":
        stream = BINANCE_FUTURES_STREAM
    elif str(candles.market).upper() == "SPOT":
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
