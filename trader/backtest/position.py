import numpy as np

from .exceptions import LiquidationError, PositionError
from trader.core.const.candle_index import CLOSE_PRICE_INDEX, LOW_PRICE_INDEX, HIGH_PRICE_INDEX
from trader.core.model import Position, Balance
from trader.core.const.trade_actions import LONG, SHORT, BUY
from trader.core.util.trade import reduce_quantity_with_fee


class BacktestPosition(Position):

    __slots__ = "times", "prices", "quantities", "__profit"

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
        self.__profit = .0

        super().__init__(symbol=symbol, quantity=entry_quantity, leverage=leverage, entry_price=entry_price)

    def __call__(self, candles: np.ndarray, balance: Balance):
        latest_candle = candles[-1]
        latest_close = latest_candle[CLOSE_PRICE_INDEX]
        latest_high = latest_candle[HIGH_PRICE_INDEX]
        latest_low = latest_candle[LOW_PRICE_INDEX]

        liquidation_profit = self.__calculate_profit(price=latest_low if self.side == BUY else latest_high)

        if liquidation_profit < 0 and abs(liquidation_profit) > balance.total:
            raise LiquidationError(f"Position liquidated! Position loss at liquidation {liquidation_profit}.")

        self.__profit = self.__calculate_profit(price=latest_close)

    def adjust(self, time: int, price: float, quantity: float):
        if self.is_closed():
            raise PositionError("Position is already closed!")

        self.times.append(time)
        self.prices.append(price)

        sum_quantity = sum(self.quantities)
        if (self.side == LONG and sum_quantity + quantity < 0) or (self.side == SHORT and sum_quantity + quantity > 0):
            quantity = -sum_quantity
        else:
            quantity = quantity

        self.quantities.append(quantity)

    def close(self, time: int, price: float):
        self.adjust(time=time, price=price, quantity=-sum(self.quantities))

    def profit(self):
        return self.__profit

    def is_closed(self):
        return sum(self.quantities) == 0

    def __calculate_profit(self, price: float = None):
        if price is None:
            price = self.prices[-1]

        costs = tuple(price * quantity for price, quantity in zip(self.prices, self.quantities))
        profits = tuple(price * quantity - cost for cost, quantity in zip(costs, self.quantities))
        sum_profit = sum(profits) * self.leverage

        return sum_profit
