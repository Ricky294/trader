import numpy as np
import talib

from trader_data.core.model import Candles
from trader_data.core.enum import OHLCV

from trader.core.enum import MA
from trader.core.indicator import Indicator


class BBANDSIndicator(Indicator):
    """Bollinger Bands"""

    color = dict(upper="#2962ff", lower="#2962ff", middle="#ff6d00")

    def __init__(
            self,
            period=5,
            std_dev_up=2,
            std_dev_down=2,
            ma=MA.SMA,
    ):
        self.period = period
        self.std_dev_up = std_dev_up
        self.std_dev_down = std_dev_down
        self.ma = ma

    def __call__(self, candles: Candles):
        """
        Calculates Bollinger Bands Indicator

        :param candles: Input data for indicator.

        :return: BBANDSResult - upper, middle, lower
        """

        self.__candles = candles
        data_line = candles.avg_line(OHLCV.HIGH_PRICE, OHLCV.LOW_PRICE, OHLCV.CLOSE_PRICE)

        self.upper_band, self.middle_band, self.lower_band = talib.BBANDS(
            data_line,
            timeperiod=self.period,
            nbdevup=self.std_dev_up,
            nbdevdn=self.std_dev_down,
            matype=int(self.ma),
        )

    def high_price_above_upper_band(self) -> np.ndarray:
        """
        True where high price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.high_prices > self.upper_band

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.close_prices > self.upper_band

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.low_prices < self.lower_band

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.close_prices < self.lower_band
