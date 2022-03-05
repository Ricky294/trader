from enum import Enum


class MAType(Enum):
    EMA = "EMA"
    WMA = "WMA"
    SMA = "SMA"

    def __str__(self):
        return self.value

    def __int__(self):
        # talib MA_Type: 0 = SMA, 1 = EMA, 2 = WMA, 3 = DEMA, 4 = TEMA, 5 = TRIMA, 6 = KAMA, 7 = MAMA, 8 = T3
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
