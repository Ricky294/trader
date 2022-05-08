import numpy as np

from trader.data.model import Candles

from trader.core.indicator import Indicator


class HeikinAshiIndicator(Indicator):
    """Heikin Ashi"""

    def __call__(self, candles: Candles):
        """
        Calculates Heikin Ashi candlesticks.

        :param candles: Input data for indicator.
        :return: HAResult - open, high, low, close
        """
        if candles.meta.get("heikin_ashi"):
            self.candles = candles
        else:
            self.candles = candles.to_heikin_ashi()

    def strong_bullish(self) -> np.ndarray:
        """
        True where open price equals with low price

        Signals buy

        :return: bool numpy array
        """
        return self.candles.open_prices == self.candles.low_prices

    def strong_bearish(self) -> np.ndarray:
        """
        True where open price equals with high price

        Signals sell

        :return: bool numpy array
        """
        return self.candles.open_prices == self.candles.high_prices

    def bullish(self) -> np.ndarray:
        """
        True where close price is greater than open price

        Signals buy

        :return: bool numpy array
        """
        return self.candles.close_prices > self.candles.open_prices

    def bearish(self) -> np.ndarray:
        """
        True where open price is greater than close price

        Signals sell

        :return: bool numpy array
        """
        return self.candles.open_prices > self.candles.close_prices
