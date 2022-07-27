from typing import Final

from trader.data.super_enum import SuperEnum


class Broker(SuperEnum):
    BINANCE: Final = 'BINANCE'
    BACKTEST: Final = 'BACKTEST'
