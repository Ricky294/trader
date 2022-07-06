from enum import Enum

from trader.config import (
    BALANCE_PRECISION,
    FEE_PRECISION,
    MONEY_PRECISION,
    PRICE_PRECISION,
    PROFIT_PRECISION,
    QUANTITY_PRECISION,
)


class PrecisionFormat(Enum):
    FEE = FEE_PRECISION
    MONEY = MONEY_PRECISION
    PRICE = PRICE_PRECISION
    PROFIT = PROFIT_PRECISION
    QUANTITY = QUANTITY_PRECISION
    BALANCE = BALANCE_PRECISION

    def __int__(self):
        return self.value
