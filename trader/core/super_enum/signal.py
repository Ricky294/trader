from typing import Final

from trader.data.super_enum import SuperEnum


class Signal(SuperEnum):
    BUY: Final = 0
    SELL: Final = 1
