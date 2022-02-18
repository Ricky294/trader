from trader.core.indicator import Indicator
from trader.core.indicator.result import IndicatorResult
from trader.core.model import Candles


class OptimizedIndicator(Indicator):

    def __init__(self, candles: Candles, indicator: Indicator):
        self.precalculated_result = indicator(candles)

    def __call__(self, candles: Candles):
        return IndicatorResult(
            **{
                name: signal[:candles.shape[0]]
                for name, signal in self.precalculated_result.__dict__.items()
            }
        )
