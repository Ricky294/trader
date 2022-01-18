from enum import Enum


class CandlestickType(Enum):
    LINE = 0
    JAPANESE = 1
    HEIKIN_ASHI = 2

    def __str__(self):
        return self.value
