import numpy as np
import pandas as pd

from trader.core.const.trade_actions import BUY, NONE, SELL


class IndicatorResult:

    def __init__(self, buy_signal: np.ndarray, sell_signal: np.ndarray, **signals: np.ndarray):
        self.buy_signal = buy_signal
        self.sell_signal = sell_signal

        for name, data in signals.items():
            self.__dict__[name] = data

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, val):
        if isinstance(val, slice):
            return np.array(tuple(signal[val.start:val.stop:val.step] for signal in self.__dict__.values()))
        else:
            return np.array(tuple(signal[val] for signal in self.__dict__.values()))

    def to_np_array(self):
        return np.array(tuple(signal for signal in self.__dict__.values()))

    def to_pd_dataframe(self):
        return pd.DataFrame(data=self.__dict__)

    def latest_buy_signal(self) -> bool:
        return bool(self.buy_signal[-1])

    def latest_sell_signal(self) -> bool:
        return bool(self.sell_signal[-1])

    def latest_signal(self) -> int:
        if self.buy_signal[-1]:
            return BUY
        elif self.sell_signal[-1]:
            return SELL
        return NONE
