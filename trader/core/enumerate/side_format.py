from enum import Enum


class SideFormat(Enum):

    NUM = 'num'
    BUY_SELL = 'buy_sell'
    LONG_SHORT = 'long_short'

    def __str__(self):
        return self.value
