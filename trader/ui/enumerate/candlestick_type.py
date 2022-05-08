from enum import Enum


class Candlestick(Enum):
    LINE = "Line"
    JAPANESE = "Japanese"
    HEIKIN_ASHI = "Heikin Ashi"

    def __str__(self):
        return self.value
