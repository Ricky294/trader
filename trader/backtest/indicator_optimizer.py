from trader.core.indicator import Indicator
from trader.core.model import Candles


class OptimizedIndicator(Indicator):

    __slots__ = "wrapped_indicator"

    def __init__(self, candles: Candles, indicator: Indicator):
        super().__init__(*indicator.additional_lines)
        indicator(candles)
        self.precalculated = indicator

    def __call__(self, candles: Candles):
        self.buy_signal = self.precalculated.buy_signal[:candles.shape[0]]
        self.sell_signal = self.precalculated.sell_signal[:candles.shape[0]]
        for key in self.additional_lines:
            self.__dict__[key] = self.precalculated.__dict__[key][:candles.shape[0]]
