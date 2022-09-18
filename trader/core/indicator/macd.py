import numpy as np
import talib

from trader.data.candle_schema import CLOSE_PRICE
from trader.data.model import Candles

from trader.core.indicator import Indicator
from trader.trade import cross


class MACDIndicator(Indicator):
    """
    Moving Average Convergence Divergence - MACD

    Momentum Indicator
    """

    def __init__(
            self,
            candles: Candles,
            line=CLOSE_PRICE,
            fast_period=12,
            slow_period=26,
            signal_period=9,
    ):
        """
        :param line: Price line to calculate MACD on.
        :param fast_period: Look-back period for MACD.
        :param slow_period: Look-back period for signal line.
        :param signal_period: Signal smoothing.
        """

        self.line = line
        self.fast_period = fast_period      # macd line
        self.slow_period = slow_period      # signal line
        self.signal_period = signal_period
        super().__init__(candles)

    @property
    def macd(self):
        return self._current_slice(self._macd)

    @property
    def signal(self):
        return self._current_slice(self._signal)

    @property
    def histogram(self):
        return self._current_slice(self._histogram)

    def __call__(self, candles: Candles):
        """
        Calculates Moving Average Convergence/Divergence (Momentum Indicator)

        :param candles: Input data for indicator.

        :return: MACDResult - macd, signal, histogram
        """

        self._macd, self._signal, self._histogram = talib.MACD(
            candles.average(self.line),
            fastperiod=self.fast_period,
            slowperiod=self.slow_period,
            signalperiod=self.signal_period,
        )

    def macd_above_zero(self) -> np.ndarray:
        """
        True where macd line is above zero.

        :return: bool numpy array
        """
        return self.macd > .0

    def macd_below_zero(self) -> np.ndarray:
        """
        True where macd line is below zero.

        :return: bool numpy array
        """
        return self.macd < .0

    def signal_above_zero(self) -> np.ndarray:
        """
        True where signal line is above zero.

        :return: bool numpy array
        """
        return self.signal > .0

    def signal_below_zero(self) -> np.ndarray:
        """
        True where signal line is above zero.

        :return: bool numpy array
        """
        return self.signal < .0

    def macd_and_signal_above_zero(self) -> np.ndarray:
        """
        True where macd and signal line is above zero.

        :return: bool numpy array
        """
        return self.macd_above_zero() & self.signal_above_zero()

    def macd_and_signal_below_zero(self) -> np.ndarray:
        """
        True where macd and signal line is below zero.

        :return: bool numpy array
        """
        return self.macd_below_zero() & self.signal_below_zero()

    def uptrend(self) -> np.ndarray:
        """
        True where macd line is above signal line.

        Indicates uptrend.

        :return: bool numpy array
        """
        return self.macd > self.signal

    def downtrend(self) -> np.ndarray:
        """
        True where macd line is below signal line.

        Indicates downtrend.

        :return: bool numpy array
        """
        return self.macd < self.signal

    def macd_cross_above_zero(self) -> np.ndarray:
        """
        True where the macd line crosses above zero.

        Same as a fast and slow EMA bullish crossover.

        Indicates uptrend.

        :return: bool numpy array
        """
        return cross(self.macd > .0)

    def macd_cross_below_zero(self) -> np.ndarray:
        """
        True where the macd line crosses below zero.

        Same as a fast and slow EMA bearish crossover.

        Indicates downtrend.

        :return: bool numpy array
        """
        return cross(self.macd < .0)

    def signal_cross_above_zero(self) -> np.ndarray:
        """
        True where the signal line crosses above zero.

        Indicates uptrend.

        :return: bool numpy array
        """
        return cross(self.signal > .0)

    def signal_cross_below_zero(self) -> np.ndarray:
        """
        True where the signal line crosses below zero.

        Indicates downtrend.

        :return: bool numpy array
        """
        return cross(self.signal < .0)

    def bullish_cross(self) -> np.ndarray:
        """
        True where the macd line crosses above the signal line.

        Same as a fast and slow EMA bullish crossover.

        Signals buy - Indicates uptrend.

        :return: bool numpy array
        """
        return cross(self.macd > self.signal)

    def bearish_cross(self) -> np.ndarray:
        """
        True where the macd line crosses below the signal line.

        Signals sell - Indicates downtrend.

        :return: bool numpy array
        """

        return cross(self.macd < self.signal)
