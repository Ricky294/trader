from enum import Enum

from trader.core.const.trade_actions import (
    BUY as BUY_,
    SELL as SELL_,
    LONG as LONG_,
    SHORT as SHORT_,
    NONE as NONE_,
)


class Signal(Enum):

    LONG = LONG_
    SHORT = SHORT_

    BUY = BUY_
    SELL = SELL_
    NONE = NONE_

    def __int__(self):
        return self.value

    def __str__(self):
        from ..util.trade import side_to_buy_sell
        return side_to_buy_sell(self.value)