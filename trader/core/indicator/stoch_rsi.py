import talib

from trader.data.model import Candles
from trader.data.enumerate import OHLCV

from trader.core.enumerate import MA
from trader.core.indicator import Indicator
from trader.core.util.vectorized.trade import cross


class STOCHRSIIndicator(Indicator):
    """Stochastic RSI"""
    def __init__(
            self,
            line=OHLCV.CLOSE_PRICE,
            upper_limit=80.0,
            lower_limit=20.0,
            period=14,
            k_period=5,
            d_period=3,
            d_ma=MA.SMA,
    ):
        """
        :param upper_limit: %D line above this limit -> overbought
        :param lower_limit: %D line below this limit -> oversold
        :param period: Stochastic and RSI period
        :param k_period: %K period
        :param d_period: %D period
        :param d_ma: %D moving average type
        """

        self.line = line
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        self.period = period
        self.k_period = k_period
        self.d_period = d_period
        self.d_ma = d_ma

    def __call__(self, candles: Candles):
        """
        Stochastic Relative Strength Index (Momentum Indicator)

        Returns the %K (fast) and %D (slow) line.

        :param candles: Input data for indicator.

        :return: STOCHRSIResult - k, d
        """

        self.k, self.d = talib.STOCHRSI(
            candles.average(self.line),
            timeperiod=self.period,
            fastk_period=self.k_period,
            fastd_period=self.d_period,
            fastd_matype=int(self.d_ma),
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
