from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count

from trader.core.exception import BalanceError
from trader.data.model import Model
from trader.settings import Settings
import util.format_util as fmt


instance_counter = count(1)


@dataclass(frozen=True, kw_only=True)
class Balance(Model):
    __count: int = field(default_factory=lambda: next(instance_counter), init=False, repr=False)

    asset: str
    total: float
    available: float

    def simple_repr(self) -> str:
        return f'{fmt.num(self.total, prec=Settings.precision_balance)} {self.asset}'

    def _validate(self, other):
        if not isinstance(other, Balance):
            raise TypeError(f'Compared value must be an instance of Balance, not {type(other).__name__}')

        if self.asset != other.asset:
            raise BalanceError(f'Cannot compare different asset balances: {self.asset!r} vs {other.asset!r}')

    def __lt__(self, other):
        self._validate(other)
        return self.total < other.total

    def __gt__(self, other):
        self._validate(other)
        return self.total > other.total

    def __le__(self, other):
        self._validate(other)
        return self.total <= other.total

    def __ge__(self, other):
        self._validate(other)
        return self.total >= other.total

    def __eq__(self, other):
        self._validate(other)
        return self.total == other.total and self.available == other.available

    def __ne__(self, other):
        return not self.__eq__(other)


if __name__ == "__main__":
    import doctest

    flags = doctest.REPORT_NDIFF | doctest.FAIL_FAST
    doctest.testmod(verbose=True)
