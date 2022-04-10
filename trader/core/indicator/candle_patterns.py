from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.util.vectorized.candlestick import *


class CandlestickPatterns(Indicator):

    __slots__ = "_open_prices", "_high_prices", "_low_prices", "_close_prices"

    def __call__(self, candles: Candles):
        self._open_prices = candles.open_prices
        self._high_prices = candles.high_prices
        self._low_prices = candles.low_prices
        self._close_prices = candles.close_prices

    def bullish(self):
        return bullish_candles(self._open_prices, self._close_prices)

    def bearish(self):
        return bearish_candles(self._open_prices, self._close_prices)

    def bullish_three_line_strike(self):
        return bullish_three_line_strike(self._open_prices, self._high_prices, self._low_prices, self._close_prices)

    def bearish_three_line_strike(self):
        return bearish_three_line_strike(self._open_prices, self._high_prices, self._low_prices, self._close_prices)

    def bullish_engulfing(self):
        return bullish_engulfing(self._open_prices, self._high_prices, self._low_prices, self._close_prices)

    def bearish_engulfing(self):
        return bearish_engulfing(self._open_prices, self._high_prices, self._low_prices, self._close_prices)

    def hammer(self):
        return hammer(self._open_prices, self._high_prices, self._low_prices, self._close_prices)

    def hanging_man(self):
        return hanging_man(self._open_prices, self._high_prices, self._low_prices, self._close_prices)
