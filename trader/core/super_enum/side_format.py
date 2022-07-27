from typing import Final

from trader.data.super_enum import SuperEnum


class SideFormat(SuperEnum):
    NUM: Final = 'NUM'
    BUY_SELL: Final = 'BUY_SELL'
    LONG_SHORT: Final = 'LONG_SHORT'
