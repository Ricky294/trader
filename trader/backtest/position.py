from trader.core.model import Position, Balance
from trader.core.const.trade_actions import LONG, SHORT


class BacktestPosition(Position):

    __slots__ = "times", "prices", "quantities"

    def __init__(
            self,
            symbol: str,
            entry_time: int,
            entry_price: float,
            entry_quantity: float,
            leverage: int,
    ):
        if entry_quantity == 0:
            raise ValueError("Quantity must not be 0!")

        self.times = [entry_time]
        self.prices = [entry_price]
        self.quantities = [entry_quantity]

        super().__init__(symbol=symbol, quantity=entry_quantity, leverage=leverage, entry_price=entry_price)

    def adjust(self, time: int, price: float, quantity: float):
        if self.is_closed():
            raise ValueError("Position is already closed!")

        self.times.append(time)
        self.prices.append(price)

        sum_quantity = sum(self.quantities) + quantity
        if (
            (self.side == LONG and sum_quantity < 0)
            or (self.side == SHORT and sum_quantity > 0)
        ):
            self.quantities.append(quantity - sum_quantity)
        else:
            self.quantities.append(quantity)

    def close(self, time: int, price: float):
        if self.is_closed():
            raise ValueError("Position is already closed!")

        self.times.append(time)
        self.prices.append(price)
        self.quantities.append(-sum(self.quantities))

    def profit(self):
        costs = tuple(price * quantity for price, quantity in zip(self.prices, self.quantities))
        profits = tuple(self.prices[-1] * quantity - cost for cost, quantity in zip(costs, self.quantities))
        sum_profit = sum(profits) * self.leverage

        return sum_profit

    def is_closed(self):
        return sum(self.quantities) == 0

    def is_liquidated(self, balance: Balance, current_price: float):
        """
        current_price: Current low or high price.
        """
        profit = calculate_profit(current_price, self)

        return profit < 0 and abs(profit) >= balance.total


def calculate_profit(price: float, pos: BacktestPosition):
    costs = tuple(price * quantity for price, quantity in zip(pos.prices, pos.quantities))
    profits = tuple(price * quantity - cost for cost, quantity in zip(costs, pos.quantities))
    sum_profit = sum(profits) * pos.leverage

    return sum_profit
