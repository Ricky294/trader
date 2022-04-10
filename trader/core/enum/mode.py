from enum import Enum


class Mode(Enum):
    BACKTEST = "backtest"
    LIVE = "live"

    def __str__(self):
        return self.value
