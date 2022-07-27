from typing import Final

from trader.data.super_enum import SuperEnum


class MA(SuperEnum):
    SMA: Final = 'SMA'
    EMA: Final = 'EMA'
    WMA: Final = 'WMA'
    DEMA: Final = 'DEMA'
    TEMA: Final = 'TEMA'
    TRIMA: Final = 'TRIMA'
    KAMA: Final = 'KAMA'
    MAMA: Final = 'MAMA'
    T3: Final = 'T3'

    def __int__(self):
        if self.value == 'SMA':
            return 0
        elif self.value == 'EMA':
            return 1
        elif self.value == 'WMA':
            return 2
        elif self.value == 'DEMA':
            return 3
        elif self.value == 'TEMA':
            return 4
        elif self.value == 'TRIMA':
            return 5
        elif self.value == 'KAMA':
            return 6
        elif self.value == 'MAMA':
            return 7
        elif self.value == 'T3':
            return 8
        return -1
