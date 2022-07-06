from __future__ import annotations

import numpy as np
import nputils as npu

from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage
from trader.data.model import Candles

from trader.core.indicator import RSIIndicator


class EntryAnalyzer:

    def __init__(self, candles: Candles, long_entries: np.ndarray, short_entries: np.ndarray, period: int):
        ls_stack = np.vstack((long_entries, short_entries))
        if True in np.all(ls_stack, axis=0):
            raise ValueError('It is forbidden to have a long and a short entry at the same time!')

        self.candles = candles
        self.long_entries = long_entries
        self.short_entries = short_entries
        self.period = period

    @property
    def all_long_entries(self):
        """
        Returns all possible entry points to go long.

        True where next and previous value is greater than current.

        :return: bool numpy array
        """
        all_long = npu.min_over_period(self.candles.open_prices)
        np.put(all_long, 0, self.candles.open_prices[0] < self.candles.open_prices[1])
        return all_long

    @property
    def all_short_entries(self):
        """
        Returns all possible entry points to go short.

        True where next and previous value is less than current.

        :return: bool numpy array
        """
        all_short = npu.max_over_period(self.candles.open_prices)
        np.put(all_short, 0, self.candles.open_prices[0] > self.candles.open_prices[1])
        return all_short

    @property
    def max_short_score(self):
        """
        Adds up all the decreasing price movement on open prices.

        :return: number
        """

        return npu.sum_decrease(self.candles.open_prices)

    @property
    def max_long_score(self):
        """
        Adds up all the increasing price movement on open prices.

        :return: number
        """

        return npu.sum_increase(self.candles.open_prices)

    @property
    def absolute_max_score(self):
        """
        Calculates the absolute total price movement on open prices.

        :return: number
        """
        return npu.absolute_change(self.candles.open_prices)

    @property
    def period_lows(self):
        return npu.min_over_period(self.candles.low_prices, self.period)

    @property
    def period_highs(self):
        return npu.max_over_period(self.candles.high_prices, self.period)

    @property
    def long_efficiencies(self):
        long_lows = self.period_lows[self.long_entries]
        long_highs = self.period_highs[self.long_entries]

        return 1 - (long_lows / long_highs)

    @property
    def avg_long_efficiency(self):
        return np.sum(self.long_efficiencies) / len(self.long_efficiencies)

    @property
    def avg_short_efficiency(self):
        return np.sum(self.short_efficiencies) / len(self.short_efficiencies)

    @property
    def avg_efficiency(self):
        return (self.avg_long_efficiency + self.avg_short_efficiency) / 2

    @property
    def short_efficiencies(self):
        short_lows = self.period_lows[self.short_entries]
        short_highs = self.period_highs[self.short_entries]

        return short_lows / short_highs


candles = get_store_candles("BTCUSDT", "1d", market="FUTURES", storage_type=HDF5CandleStorage)
rsi_ind = RSIIndicator(lower_limit=25, upper_limit=75)
rsi_ind(candles)

ea = EntryAnalyzer(
    candles=candles,
    short_entries=rsi_ind.overbought_reversal(),
    long_entries=rsi_ind.oversold_reversal(),
    period=30,
)

