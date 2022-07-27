from typing import Final

from trader.data.super_enum import SuperEnum


class OrderType(SuperEnum):
    MARKET: Final = 'MARKET'
    LIMIT: Final = 'LIMIT'
    STOP_MARKET: Final = 'STOP_MARKET'
    STOP_LIMIT: Final = 'STOP_LIMIT'
    TAKE_PROFIT_MARKET: Final = 'TAKE_PROFIT_MARKET'
    TAKE_PROFIT_LIMIT: Final = 'TAKE_PROFIT_LIMIT'
    TRAILING_STOP_MARKET: Final = 'TRAILING_STOP_MARKET'

    def is_taker(self):
        """
        Does not go into the order book (instantly executed).

        Market type order.
        """
        return 'MARKET' in self.value

    def is_maker(self):
        """
        Goes into the order book (not instantly executed).

        Limit type order.
        """
        return 'LIMIT' in self.value

    def __int__(self):
        if self.value == 'MARKET':
            return 0
        elif self.value == 'LIMIT':
            return 1
        elif self.value == 'STOP_MARKET':
            return 2
        elif self.value == 'STOP_LIMIT':
            return 3
        elif self.value == 'TAKE_PROFIT_MARKET':
            return 4
        elif self.value == 'TAKE_PROFIT_LIMIT':
            return 5
        elif self.value == 'TRAILING_STOP_MARKET':
            return 6
        raise ValueError(f'Invalid value: {self.value}')
