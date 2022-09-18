from typing import Final

from util.super_enum import SuperEnum


class Broker(SuperEnum):
    BINANCE: Final = 'BINANCE'
    BACKTEST: Final = 'BACKTEST'

    def url(self) -> str | None:
        if self is Broker.BINANCE:
            return 'https://www.binance.com/en'
