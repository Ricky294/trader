from enum import Enum


class MA(Enum):
    SMA = "SMA"
    EMA = "EMA"
    WMA = "WMA"
    DEMA = "DEMA"
    TEMA = "TEMA"
    TRIMA = "TRIMA"
    KAMA = "KAMA"
    MAMA = "MAMA"
    T3 = "T3"

    def __str__(self):
        return self.value

    def __int__(self):
        if self.value == "SMA":
            return 0
        elif self.value == "EMA":
            return 1
        elif self.value == "WMA":
            return 2
        elif self.value == "DEMA":
            return 3
        elif self.value == "TEMA":
            return 4
        elif self.value == "TRIMA":
            return 5
        elif self.value == "KAMA":
            return 6
        elif self.value == "MAMA":
            return 7
        elif self.value == "T3":
            return 8
