import numpy as np

from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import to_heikin_ashi


class HeikinAshiIndicator(Indicator):
    """Heikin Ashi"""

    def __call__(self, candles: Candles):
        """
        Calculates Heikin Ashi candlesticks.

        :param candles: Input data for indicator.
        :return: HAResult - open, high, low, close
        """

        self.ha_open, self.ha_high, self.ha_low, self.ha_close = to_heikin_ashi(
            open=candles.open_prices,
            high=candles.high_prices,
            low=candles.low_prices,
            close=candles.close_prices,
        )

    def strong_bullish(self) -> np.ndarray:
        """
        True where open price equals with low price

        Signals buy

        :return: bool numpy array
        """
        return self.ha_open == self.ha_low

    def strong_bearish(self) -> np.ndarray:
        """
        True where open price equals with high price

        Signals sell

        :return: bool numpy array
        """
        return self.ha_open == self.ha_high

    def bullish(self) -> np.ndarray:
        """
        True where close price is greater than open price

        Signals buy

        :return: bool numpy array
        """
        return self.ha_close > self.ha_open

    def bearish(self) -> np.ndarray:
        """
        True where open price is greater than close price

        Signals sell

        :return: bool numpy array
        """
        return self.ha_open > self.ha_close
