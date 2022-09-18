import numpy as np
import talib

from trader.data.model import Candles
from trader.data.candle_schema import HIGH_PRICE, LOW_PRICE, CLOSE_PRICE

from trader.core.const import MA
from trader.core.indicator import Indicator


class BBANDSIndicator(Indicator):
    """
    Bollinger Bands - BBANDS

    Overlap Studies
    """

    color = dict(upper="#2962ff", lower="#2962ff", middle="#ff6d00")

    def __init__(
            self,
            candles: Candles,
            period=5,
            std_dev_up=2,
            std_dev_down=2,
            ma: MA = MA.SMA,
    ):
        self.period = period
        self.std_dev_up = std_dev_up
        self.std_dev_down = std_dev_down
        self.ma = ma
        super().__init__(candles)

    @property
    def upper_band(self):
        return self._current_slice(self._upper_band)

    @property
    def middle_band(self):
        return self._current_slice(self._middle_band)

    @property
    def lower_band(self):
        return self._current_slice(self._lower_band)

    def __call__(self, candles: Candles):
        """
        Calculates Bollinger Bands Indicator

        :param candles: Input data for indicator.

        :return: BBANDSResult - upper, middle, lower
        """

        self._candles = candles

        self._upper_band, self._middle_band, self._lower_band = talib.BBANDS(
            candles.average(HIGH_PRICE, LOW_PRICE, CLOSE_PRICE),
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
        return self.candles.high_prices > self.upper_band

    def close_price_above_upper_band(self) -> np.ndarray:
        """
        True where close price is above upper band.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.candles.close_prices > self.upper_band

    def low_price_below_lower_band(self) -> np.ndarray:
        """
        True where low price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.candles.low_prices < self.lower_band

    def close_price_below_lower_band(self) -> np.ndarray:
        """
        True where close price is below lower band.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.candles.close_prices < self.lower_band
