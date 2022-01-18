from enum import Enum


class MAType(Enum):
    EMA = "EMA"
    WMA = "WMA"
    SMA = "SMA"

    def __str__(self):
        return self.value
