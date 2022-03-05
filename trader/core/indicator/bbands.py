import numpy as np
import talib

from trader.core.enum import OHLCV, MAType
from trader.core.indicator import Indicator, Result
from trader.core.model import Candles
from trader.core.util.np import avg_line


class BBANDSResult(Result):

    def __init__(self, upper: np.ndarray, middle: np.ndarray, lower: np.ndarray, candles: Candles):
        self.upper = upper
        self.middle = middle
        self.lower = lower
        self.__candles = candles

    def high_price_above_upper_band(self) -> np.ndarray:
        """
        True where high price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.high_prices() > self.upper

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.__candles.close_prices() > self.upper

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.low_prices() < self.lower

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.__candles.close_prices() < self.lower


class BBANDSIndicator(Indicator):

    def __init__(
            self,
            period=5,
            std_dev_up=2,
            std_dev_down=2,
            ma=MAType.SMA,
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

        candles = candles
        data_line = avg_line(candles=candles, line=tuple((OHLCV.HIGH_PRICE, OHLCV.LOW_PRICE, OHLCV.CLOSE_PRICE)))

        upper, middle, lower = talib.BBANDS(
            data_line,
            timeperiod=self.period,
            nbdevup=self.std_dev_up,
            nbdevdn=self.std_dev_down,
            matype=int(self.ma),
        )

        return BBANDSResult(
            upper=upper,
            middle=middle,
            lower=lower,
            candles=candles,
        )
