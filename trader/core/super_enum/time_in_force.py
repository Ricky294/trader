from typing import Final

from trader.data.super_enum import SuperEnum


class TimeInForce(SuperEnum):
    GTC: Final = 'GTC'
    IOC: Final = 'IOC'
    FOK: Final = 'FOK'
    GTX: Final = 'GTX'
