from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.util.vectorized.common import local_min, local_max


class DonchianChannelsIndicator(Indicator):

    def __init__(self, period):
        self.period = period

    def __call__(self, candles: Candles):
        self._candles = candles
        self.lower_channel = local_min(candles.low_prices, self.period)
        self.upper_channel = local_max(candles.high_prices, self.period)
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
