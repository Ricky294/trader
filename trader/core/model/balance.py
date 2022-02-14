from trader.core.exception import BalanceError


class Balance:

    __slots__ = "asset", "free"

    def __init__(self, asset: str, free: float):
        if float(free) <= 0:
            raise BalanceError(f"{asset!r} balance must be greater than 0.")

        self.asset = str(asset)
        self.free = float(free)

    def __str__(self):
        return f"{self.free} {self.asset}"
