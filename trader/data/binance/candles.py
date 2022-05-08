from __future__ import annotations

from typing import Callable

import numpy as np

from trader.data.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE
from trader.data.binance import (
    candle_stream, get_candles_as_array, CLOSE_TIME, QUOTE_ASSET_VOLUME, NUMBER_OF_TRADES,
    TAKER_BUY_BASE_ASSET_VOLUME, TAKER_BUY_QUOTE_ASSET_VOLUME
)

from trader.data.enum import Market
from trader.data.model import Candles


class BinanceCandles(Candles):
    """
    Suitable to store binance candles.

    Schema:
        - OPEN_TIME
        - OPEN_PRICE
        - HIGH_PRICE
        - LOW_PRICE
        - CLOSE_TIME
        - VOLUME
        - CLOSE_TIME
        - QUOTE_ASSET_VOLUME
        - NUMBER_OF_TRADES
        - TAKER_BUY_BASE_ASSET_VOLUME
        - TAKER_BUY_QUOTE_ASSET_VOLUME
    """
    def __init__(
            self,
            candles: np.ndarray,
            symbol: str,
            interval: str,
            market: str | Market,
            schema=(
                OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE,
                CLOSE_TIME, QUOTE_ASSET_VOLUME, NUMBER_OF_TRADES,
                TAKER_BUY_QUOTE_ASSET_VOLUME, TAKER_BUY_BASE_ASSET_VOLUME
            )
    ):
        super().__init__(candles=candles, symbol=symbol, interval=interval, market=market, schema=schema)

    def start_candle_stream(
            self,
            on_candle_close: Callable[[Candles], any],
            on_candle: Callable[[dict], any],
            log_candles=True
    ):
        candle_stream(
            candles=self,
            on_candle_close=on_candle_close,
            on_candle=on_candle,
            log_candles=log_candles,
        )

    def update(self):
        latest_open = self.open_times[-1] + 1

        missing_candles = get_candles_as_array(
            symbol=self.symbol,
            interval=self.interval,
            market=self.market,
            start_ts=latest_open,
            columns=self.schema,
        )

        self.concatenate(missing_candles)

    @property
    def close_times(self) -> np.ndarray | None:
        try:
            return self.__getitem__(CLOSE_TIME)
        except ValueError:
            return None

    @property
    def latest_close_time(self):
        try:
            return self.close_times[-1]
        except TypeError:
            return None

    @property
    def quote_asset_volumes(self) -> np.ndarray | None:
        try:
            return self.__getitem__(QUOTE_ASSET_VOLUME)
        except ValueError:
            return None

    @property
    def latest_quote_asset_volumes(self):
        try:
            return self.quote_asset_volumes[-1]
        except TypeError:
            return None

    @property
    def number_of_trades(self) -> np.ndarray | None:
        try:
            return self.__getitem__(NUMBER_OF_TRADES)
        except ValueError:
            return None

    @property
    def latest_number_of_trades(self):
        try:
            return self.number_of_trades[-1]
        except TypeError:
            return None

    @property
    def taker_buy_base_asset_volumes(self) -> np.ndarray | None:
        try:
            return self.__getitem__(TAKER_BUY_BASE_ASSET_VOLUME)
        except ValueError:
            return None

    @property
    def latest_taker_buy_base_asset_volumes(self):
        try:
            return self.taker_buy_base_asset_volumes[-1]
        except TypeError:
            return None

    @property
    def taker_buy_quote_asset_volumes(self) -> np.ndarray | None:
        try:
            return self.__getitem__(TAKER_BUY_QUOTE_ASSET_VOLUME)
        except ValueError:
            return None

    @property
    def latest_taker_buy_quote_asset_volumes(self):
        try:
            return self.taker_buy_quote_asset_volumes[-1]
        except TypeError:
            return None
