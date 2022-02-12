from trader.core.model import Balance


class BacktestBalance(Balance):

    def __init__(self, asset: str, amount: float):
        super().__init__(asset, amount)
