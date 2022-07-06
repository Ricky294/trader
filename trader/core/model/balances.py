from typing import Iterable

import numpy as np

from trader.core.model import Balance
from trader.data.model import Columnar


class Balances(Columnar):

    def __init__(self, balances: Iterable[Balance]):
        super().__init__()
        balances = list(balances)

        def pnl():
            return np.array([
                0 if i == 0 else balances[i].free - balances[i - 1].free
                for i in range(len(balances))
            ])

        self.time = [balance.time for balance in balances]
        self.asset = [balance.asset for balance in balances]
        self.balance = [balance.free for balance in balances]
        self.profit = pnl()
