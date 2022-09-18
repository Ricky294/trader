import nputils as npu

from trader.data.model import Candles

from trader.core.indicator import Indicator


class DonchianChannelsIndicator(Indicator):
    """
    Donchian Channels - DONC

    """

    def __init__(self, candles: Candles, period: int):
        self.period = period
        super().__init__(candles)

    def __call__(self, candles: Candles):
        self._candles = candles
        self._lower_channel = npu.min_over_period(candles.low_prices, self.period)
        self._upper_channel = npu.max_over_period(candles.high_prices, self.period)
        self._middle_channel = (self._upper_channel + self._lower_channel) / 2

    @property
    def lower_channel(self):
        return self._current_slice(self._lower_channel)

    @property
    def middle_channel(self):
        return self._current_slice(self._middle_channel)

    @property
    def upper_channel(self):
        return self._current_slice(self._upper_channel)

    def price_touches_upper_channel(self):
        return self.candles.high_prices >= self.upper_channel

    def price_touches_lower_channel(self):
        return self.candles.low_prices <= self.lower_channel

    def open_above_middle_channel(self):
        return self.candles.open_prices > self.middle_channel

    def high_above_middle_channel(self):
        return self.candles.high_prices > self.middle_channel

    def low_above_middle_channel(self):
        return self.candles.low_prices > self.middle_channel

    def close_above_middle_channel(self):
        return self.candles.close_prices > self.middle_channel

    def open_below_middle_channel(self):
        return self.candles.open_prices < self.middle_channel

    def high_below_middle_channel(self):
        return self.candles.high_prices < self.middle_channel

    def low_below_middle_channel(self):
        return self.candles.low_prices < self.middle_channel

    def close_below_middle_channel(self):
        return self.candles.close_prices < self.middle_channel
