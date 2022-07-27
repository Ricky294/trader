from typing import Final

from trader.data.super_enum import SuperEnum


class Mode(SuperEnum):
    BACKTEST: Final = 'BACKTEST'
    LIVE: Final = 'LIVE'
