from trader.core.model import Balance


class BinanceBalance(Balance):

    def __init__(self, time: int, asset: str, total: float, available: float):
        super().__init__(time=time, asset=asset, available=available)
        self.total = float(total)

    def used(self):
        return abs(self.available - self.total)

