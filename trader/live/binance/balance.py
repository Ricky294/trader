from trader.core.model import Balance


class BinanceBalance(Balance):

    def __init__(self, time: int, asset: str, total: float, free: float):
        super().__init__(time=time, asset=asset, free=free)
        self.total = float(total)

    def used(self):
        return abs(self.free - self.total)

