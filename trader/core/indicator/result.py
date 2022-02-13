import numpy as np

from trader.core.const.trade_actions import BUY, SELL, NONE


class _AdditionalIndicatorData:

    def __init__(self, **lines):
        for key, val in lines.items():
            self.__dict__[key] = val


class IndicatorResult(_AdditionalIndicatorData):

    __slots__ = "buy_signal", "sell_signal"

    def __init__(self, buy_signal: np.ndarray, sell_signal: np.ndarray, **lines: np.ndarray):
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal
        super(IndicatorResult, self).__init__(**lines)

    def latest_signal(self) -> int:
        if self.buy_signal[-1]:
            return BUY
        elif self.sell_signal[-1]:
            return SELL
        return NONE
