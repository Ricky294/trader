from trader.core.model import Balance


class BinanceBalance(Balance):

    __slots__ = 'total'

    def __init__(self, asset: str, total: float, free: float):
        super().__init__(asset=asset, free=free)
        self.total = float(total)

    def used(self):
        return abs(self.free - self.total)

    def __str__(self):
        return f'{self}, (free: {self.free})'
