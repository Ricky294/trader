from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Final

from trader.core.const import Side, BrokerEvent
from trader.data.model import Model, Symbol

POSITION_CLOSE: Final = -1
POSITION_ENTRY: Final = 0

instance_counter = count(1)


@dataclass(frozen=True, kw_only=True)
class Position(Model):
    __count: int = field(default_factory=lambda: next(instance_counter), init=False, repr=False)

    symbol: Symbol
    side: Side
    leverage: int
    amount: float
    quantity: float
    price: float
    fee: float
    state: int
    profit: float

    @property
    def is_open(self):
        return self.state != POSITION_CLOSE

    @property
    def is_close(self):
        return self.state == POSITION_CLOSE

    @property
    def is_entry(self):
        return self.state == POSITION_ENTRY

    @property
    def is_adjust(self):
        return self.state > 0

    def event(self):
        if self.state == POSITION_ENTRY:
            return BrokerEvent.ON_POSITION_OPEN
        elif self.state == POSITION_CLOSE:
            return BrokerEvent.ON_POSITION_CLOSE
        return BrokerEvent.ON_POSITION_ADJUST
