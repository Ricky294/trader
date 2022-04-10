from trader_data.core.model import Candles

from trader.core.indicator import Indicator
from trader.core.interface import FuturesTrader
from trader.core.strategy import Strategy


class IndicatorStrategy(Strategy):

    def __init__(self, trader: FuturesTrader, *indicators: Indicator):
        super().__init__(trader)
        self.indicators = indicators
        self.candles = None

    def on_next(self, candles: Candles):
        self.candles = candles
        for indicator in self.indicators:
            indicator(candles)
