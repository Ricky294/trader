from trader.config import MONEY_PRECISION
from trader.core.exception import BalanceError


class Balance:

    __slots__ = "asset", "free"

    def __init__(self, asset: str, free: float):
        if float(free) < 0:
            raise BalanceError(f"{asset!r} balance must be greater than 0.")

        self.asset = asset
        self.free = float(free)

    def __str__(self):
        return f"{self.free:.{MONEY_PRECISION}f} {self.asset}"

    def __check_asset(self, other):
        if other.asset != self.asset:
            raise BalanceError(f"Unable to add different assets: {other.asset!r} with {self.asset!r}")

    def __eq__(self, other):
        return isinstance(other, Balance) and self.asset == other.asset and self.free == other.free

    def __ne__(self, other):
        return not self.__eq__(other)

    def __iadd__(self, other):
        if isinstance(other, Balance):
            self.__check_asset(other)
            self.free += other.free

        self.free += float(other)
        return self

    def __add__(self, other):
        if isinstance(other, Balance):
            self.__check_asset(other)
            return type(self)(asset=self.asset, free=self.free + other.free)

        return type(self)(asset=self.asset, free=self.free + float(other))

    def __isub__(self, other):
        if isinstance(other, Balance):
            self.__check_asset(other)
            self.free -= other.free

        self.free -= float(other)
        return self

    def __sub__(self, other):
        if isinstance(other, Balance):
            self.__check_asset(other)
            return type(self)(asset=self.asset, free=self.free - other.free)

        return type(self)(asset=self.asset, free=self.free - float(other))
