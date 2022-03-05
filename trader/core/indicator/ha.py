import numpy as np

from trader.core.model import Candles
from trader.core.indicator import Indicator, Result
from trader.core.util.trade import to_heikin_ashi


class HAResult(Result):

    def __init__(self, open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
        self.open = open
        self.high = high
        self.low = low
        self.close = close

    def strong_bullish(self) -> np.ndarray:
        """
        True where open price equals with low price

        Signals buy

        :return: bool numpy array
        """
        return self.open == self.low

    def strong_bearish(self) -> np.ndarray:
        """
        True where open price equals with high price

        Signals sell

        :return: bool numpy array
        """
        return self.open == self.high

    def bullish(self) -> np.ndarray:
        """
        True where close price is greater than open price

        Signals buy

        :return: bool numpy array
        """
        return self.close > self.open

    def bearish(self) -> np.ndarray:
        """
        True where open price is greater than close price

        Signals sell

        :return: bool numpy array
        """
        return self.open > self.close


class HeikinAshiIndicator(Indicator):

    def __call__(self, candles: Candles):
        """
        Calculates Heikin Ashi candlesticks.

        :param candles: Input data for indicator.
        :return: HAResult - open, high, low, close
        """

        ha_open, ha_high, ha_low, ha_close = to_heikin_ashi(
            open=candles.open_prices(),
            high=candles.high_prices(),
            low=candles.low_prices(),
            close=candles.close_prices(),
        )

        return HAResult(
            open=ha_open,
            high=ha_high,
            low=ha_low,
            close=ha_close,
        )
