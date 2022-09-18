from typing import Final

from util.super_enum import SuperEnum


class Environment(SuperEnum):
    BACKTEST: Final = 'BACKTEST'
    BINANCE: Final = 'BINANCE'

    def is_live(self) -> bool:
        return self in (Environment.BINANCE,)
