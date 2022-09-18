from __future__ import annotations

from trader.data.model import Candles
from trader.data.candle_schema import CLOSE_PRICE

from trader.core.const import MA
from trader.core.indicator import Indicator
from trader.trade import talib_ma


class MAIndicator(Indicator):
    """
    Moving Average - MA

    Overlap Studies
    """

    color = {"fast_ma": "#00bcd4", "slow_ma": "#f23645"}

    def __init__(
            self,
            candles: Candles,
            period: int,
            type: MA,
            line=CLOSE_PRICE,
    ):
        self.period = period
        self.type = type
        self.line = line
        super().__init__(candles)

    @property
    def ma(self):
        return self._current_slice(self._ma)

    def __call__(self, candles: Candles):
        """
        Calculates moving average.
        """
        self._candles = candles
        self._ma = talib_ma(
            candles.average(self.line),
            type=self.type,
            period=self.period,
        )

    def below_low_price(self):
        return self.ma < self.candles.low_prices

    def below_close_price(self):
        return self.ma < self.candles.close_prices

    def below_high_price(self):
        return self.ma < self.candles.high_prices

    def below_open_price(self):
        return self.ma < self.candles.open_prices

    def above_low_price(self):
        return self.ma > self.candles.low_prices

    def above_close_price(self):
        return self.ma > self.candles.close_prices

    def above_high_price(self):
        return self.ma > self.candles.high_prices

    def above_open_price(self):
        return self.ma > self.candles.open_prices
