import talib

from trader.data.model import Candles

from trader.core.super_enum import MA
from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import cross


class STOCHIndicator(Indicator):
    """Stochastic"""

    color = {"k": "#", "d": "#"}

    def __init__(
            self,
            upper_limit=80.0,
            lower_limit=20.0,
            fast_k_period=5,
            slow_k_period=3,
            slow_k_ma: MA = MA.SMA,
            slow_d_period=3,
            slow_d_ma: MA = MA.SMA,
    ):
        """
        :param upper_limit: %D line above this limit -> overbought
        :param lower_limit: %D line below this limit -> oversold
        :param fast_k_period: %K period
        :param slow_k_period: %K smoothing period
        :param slow_k_ma: %K smoothing moving average type
        :param slow_d_period: %D smoothing period
        :param slow_d_ma: %D smoothing moving average type
        """

        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.fast_k_period = fast_k_period
        self.slow_k_period = slow_k_period
        self.slow_k_ma = slow_k_ma
        self.slow_d_period = slow_d_period
        self.slow_d_ma = slow_d_ma

    def __call__(self, candles: Candles):
        """
        Stochastic (Momentum Indicator)

        Returns the %K (fast) and %D (slow) line.

        :param candles: Input data for indicator.

        :return: STOCHResult - k, d
        """
        self.k, self.d = talib.STOCH(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            fastk_period=self.fast_k_period,
            slowk_period=self.slow_k_period,
            slowk_matype=int(self.slow_k_ma),
            slowd_period=self.slow_d_period,
            slowd_matype=int(self.slow_d_ma),
        )

    def above_upper_limit(self):
        """
        True where both %K and %D line is above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.fast_line_above_upper_limit() & self.slow_line_above_upper_limit()

    def below_lower_limit(self):
        """
        True where both %K and %D line is below lower limit.

        Overbought - Signals buy

        :return: bool numpy array
        """
        return self.fast_line_below_lower_limit() & self.slow_line_below_lower_limit()

    def fast_line_above_upper_limit(self):
        """
        True where %K line is above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.k > self.upper_limit

    def slow_line_above_upper_limit(self):
        """
        True where %D line is above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.d > self.upper_limit

    def fast_line_below_lower_limit(self):
        """
        True where %K line is below lower limit.

        Overbought - Signals buy

        :return: bool numpy array
        """
        return self.k < self.lower_limit

    def slow_line_below_lower_limit(self):
        """
        True where %D line is below lower limit.

        Overbought - Signals buy

        :return: bool numpy array
        """
        return self.d < self.lower_limit

    def bullish_cross(self):
        """
        True where %K crosses above %D.

        Uptrend - Signals buy

        :return: bool numpy array
        """
        return cross(self.k > self.d)

    def bearish_cross(self):
        """
        True where %K crosses below %D.

        Downtrend - Signals sell

        :return: bool numpy array
        """
        return cross(self.k < self.d)

    def bullish_cross_below_limit(self):
        """
        True where %K crosses above %D below lower limit.

        Uptrend - Signals buy

        :return: bool numpy array
        """
        return self.bullish_cross() & (self.k < self.lower_limit)

    def bearish_cross_above_limit(self):
        """
        True where %K crosses below %D above lower limit.

        Downtrend - Signals sell

        :return: bool numpy array
        """
        return self.bearish_cross() & (self.k > self.upper_limit)

