from typing import Iterable

import trader.core.const.signal as signal

from util.super_enum import SuperEnum


class Side(SuperEnum):
    BUY = LONG = signal.BUY
    SELL = SHORT = signal.SELL

    @classmethod
    def from_value(cls, side: int | str):
        if side in [signal.BUY, 'BUY', 'LONG']:
            return Side.BUY
        elif side in [signal.SELL, 'SELL', 'SHORT']:
            return Side.SELL

        raise ValueError(
            f'{side!r} is not a valid value. '
            f'Valid values are: {cls.keys()}'
        )

    def to_long_short(self):
        return 'LONG' if self.value is signal.BUY else 'SHORT'

    def to_buy_sell(self):
        return 'BUY' if self.value is signal.BUY else 'SELL'

    def opposite(self):
        return Side.BUY if self is Side.SELL else Side.SELL

    def __str__(self):
        from trader.core.const import Market
        from trader.settings import Settings
        return self.to_long_short() if Settings.market is Market.FUTURES else self.to_buy_sell()

    def __repr__(self):
        from trader.core.const import Market
        from trader.settings import Settings
        val = self.to_long_short() if Settings.market is Market.FUTURES else self.to_buy_sell()
        return repr(val)

    def __int__(self):
        return int(self.value)


def side_to_long_short(sides: Iterable[Side]):
    return [side.to_long_short() for side in sides]


def side_to_buy_sell(sides: Iterable[Side]):
    return [side.to_buy_sell() for side in sides]


def side_to_int(sides: Iterable[Side]):
    return [int(side) for side in sides]
