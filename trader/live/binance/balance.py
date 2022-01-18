from trader.core.model import Balance


class BinanceBalance(Balance):

    def __init__(self, asset: str, total: float, available: float):
        super().__init__(asset=asset, total=total, available=available)
