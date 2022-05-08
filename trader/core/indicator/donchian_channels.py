import nputils as npu

from trader.data.model import Candles

from trader.core.indicator import Indicator


class DonchianChannelsIndicator(Indicator):

    def __init__(self, period):
        self.period = period

    def __call__(self, candles: Candles):
        self._candles = candles
        self.lower_channel = npu.min_over_period(candles.low_prices, self.period)
        self.upper_channel = npu.max_over_period(candles.high_prices, self.period)
        self.middle_channel = (self.upper_channel + self.lower_channel) / 2

    def price_touches_upper_channel(self):
        return self._candles.high_prices >= self.upper_channel

    def price_touches_lower_channel(self):
        return self._candles.low_prices <= self.lower_channel

    def open_above_middle_channel(self):
        return self._candles.open_prices > self.middle_channel

    def high_above_middle_channel(self):
        return self._candles.high_prices > self.middle_channel

    def low_above_middle_channel(self):
        return self._candles.low_prices > self.middle_channel

    def close_above_middle_channel(self):
        return self._candles.close_prices > self.middle_channel

    def open_below_middle_channel(self):
        return self._candles.open_prices < self.middle_channel

    def high_below_middle_channel(self):
        return self._candles.high_prices < self.middle_channel

    def low_below_middle_channel(self):
        return self._candles.low_prices < self.middle_channel

    def close_below_middle_channel(self):
        return self._candles.close_prices < self.middle_channel
