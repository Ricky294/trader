import numpy as np
import talib

from trader.data.model import Candles

from trader.core.indicator import Indicator
from trader.trade import cross


class ADXIndicator(Indicator):
    """
    Average Directional Movement Index

    Momentum Indicator
    """

    def __init__(self, candles: Candles, adx_period=14):
        self.adx_period = adx_period
        super().__init__(candles)

    @property
    def adx(self):
        return self._current_slice(self._adx)

    def __call__(self, candles: Candles):
        """
        Calculates Average Directional Movement Index (Momentum Indicator)

        :param candles: Input data for indicator.

        :return: ADXResult - adx
        """

        self._adx = talib.ADX(
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
