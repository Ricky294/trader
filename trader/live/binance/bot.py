from typing import Union, Iterable

import numpy as np
import pandas as pd

from crypto_data.binance.np.stream import candle_stream
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from crypto_data.enum.market import Market

from ...core.interface import TradingBot
from ...core.strategy import Strategy
from ..binance import BinanceFuturesTrader


class BinanceBot(TradingBot):

    def __init__(
            self,
            candles: Union[np.ndarray, pd.DataFrame, Iterable],
            strategy: Strategy,
    ):
        if not isinstance(strategy.trader, (BinanceFuturesTrader,)):
            raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

        super().__init__(candles, strategy)

    def run(
            self,
            symbol: str,
            interval: str,
            market: Union[str, Market],
    ):
        candle_stream(
            symbol=symbol,
            interval=interval,
            market=str(market),
            columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
            candles=self.candles,
            on_candle=lambda stream_candle: None,
            on_candle_close=self.strategy,
        )
