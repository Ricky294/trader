import numpy as np
import talib

from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import cross


class ADXIndicator(Indicator):
    """Average Directional Movement Index"""

    def __init__(self, adx_period=14, volatility_limit=25.0):
        self.adx_period = adx_period
        self.volatility_limit = volatility_limit

    def __call__(self, candles: Candles):
        """
        Calculates Average Directional Movement Index (Momentum Indicator)

        :param candles: Input data for indicator.

        :return: ADXResult - adx
        """

        self.adx = talib.ADX(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            self.adx_period
        )

    def ranging(self) -> np.ndarray:
        """
        True where ADX is above volatility limit.

        Indicates a ranging market.

        :return: bool numpy array
        """
        return self.adx < self.volatility_limit

    def trending(self) -> np.ndarray:
        """
        True where ADX is above volatility limit.

        Indicates a trending market.

        :return: bool numpy array
        """
        return self.adx > self.volatility_limit

    def cross_to_trending(self):
        """
        True where ADX crosses above volatility limit.

        Indicates a trending market.

        :return: bool numpy array
        """
        return cross(self.adx > self.volatility_limit)

    def cross_from_trending(self):
        """
        True where ADX crosses below volatility limit.

        Indicates a ranging market.

        :return: bool numpy array
        """
        return cross(self.adx < self.volatility_limit)
