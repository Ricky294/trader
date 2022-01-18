import logging

import numpy as np

from trader.core.indicator import EntryIndicator


class IndicatorOptimizer(EntryIndicator):
    def __init__(self, all_candles: np.ndarray, indicator: EntryIndicator):
        self.indicator = indicator
        self._result = indicator(all_candles).T

    def __call__(self, candles: np.ndarray):
        next_data = self._result[:candles.shape[0]]
        return next_data.T

    def save_object(self, filename):
        return self.indicator.save_object(filename)

    def log(self, logger: logging.Logger, level=logging.INFO):
        return self.indicator.log(logger, level)

    def dict(self):
        return self.indicator.dict()

    def __str__(self):
        return self.indicator.__str__()
