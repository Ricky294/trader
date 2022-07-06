from typing import Iterable

import numpy as np

from trader.core.const.trade_actions import LONG, SHORT
from trader.core.model import Position
from trader.data.model import Columnar


class Positions(Columnar):

    def __init__(self, positions: Iterable[Position]):
        super().__init__()
        self.symbol = np.array([pos.symbol for pos in positions])

        self.side = np.array([pos.side for pos in positions])
        self.money = np.array([pos.money for pos in positions])
        self.quantity = np.array([pos.quantity for pos in positions])
        self.leverage = np.array([pos.leverage for pos in positions])

        self.entry_time = np.array([pos.entry_time for pos in positions])
        self.entry_price = np.array([pos.entry_price for pos in positions])
        self.entry_fee = np.array([pos.entry_fee for pos in positions])

        self.exit_time = np.array([pos.exit_time for pos in positions])
        self.exit_price = np.array([pos.exit_price for pos in positions])
        self.exit_fee = np.array([pos.exit_fee for pos in positions])
        self.profit = np.array([pos.profit for pos in positions])

    @property
    def long_entry_time(self):
        return self.entry_time[self.side == LONG]

    @property
    def long_entry_price(self):
        return self.entry_price[self.side == LONG]

    @property
    def long_side(self):
        return self.side[self.side == LONG]

    @property
    def long_money(self):
        return self.money[self.side == LONG]

    @property
    def long_quantity(self):
        return self.quantity[self.side == LONG]

    @property
    def long_entry_fee(self):
        return self.entry_fee[self.side == LONG]

    @property
    def short_entry_time(self):
        return self.entry_time[self.side == SHORT]

    @property
    def short_entry_price(self):
        return self.entry_price[self.side == SHORT]

    @property
    def short_side(self):
        return self.side[self.side == SHORT]

    @property
    def short_money(self):
        return self.money[self.side == SHORT]

    @property
    def short_quantity(self):
        return self.quantity[self.side == SHORT]

    @property
    def short_entry_fee(self):
        return self.entry_fee[self.side == SHORT]

    @property
    def long_exit_time(self):
        return self.exit_time[self.side == LONG]

    @property
    def short_exit_time(self):
        return self.exit_time[self.side == SHORT]

    @property
    def long_exit_price(self):
        return self.exit_price[self.side == LONG]

    @property
    def short_exit_price(self):
        return self.exit_price[self.side == SHORT]

    @property
    def long_exit_fee(self):
        return self.exit_fee[self.side == LONG]

    @property
    def short_exit_fee(self):
        return self.exit_fee[self.side == SHORT]

    @property
    def long_profit(self):
        return self.profit[self.side == LONG]

    @property
    def short_profit(self):
        return self.profit[self.side == SHORT]

    @property
    def positive_profit(self):
        return self.profit[self.profit >= 0]

    @property
    def negative_profit(self):
        return self.profit[self.profit < 0]

    @property
    def positive_profit_time(self):
        return self.exit_time[self.profit >= 0]

    @property
    def negative_profit_time(self):
        return self.exit_time[self.profit < 0]

    @property
    def win_rate(self):
        """
        Number of winning trades / number of trades

        :return: float between 0 and 1
        """
        try:
            return self.number_of_wins / self.number_of_trades
        except ZeroDivisionError:
            return .0

    @property
    def win_percentage(self):
        """
        Number of winning trades / number of trades * 100

        :return: float between 0 and 100
        """
        return self.win_rate * 100

    @property
    def loss_rate(self):
        """
        Number of loosing trades / number of trades

        :return: float between 0 and 1
        """
        try:
            return self.number_of_losses / self.number_of_trades
        except ZeroDivisionError:
            return .0

    @property
    def loss_percentage(self):
        """
        Number of loosing trades / number of trades * 100

        :return: float between 0 and 100
        """
        return self.loss_rate * 100

    @property
    def largest_profit(self) -> float:
        """
        Returns the largest profit of all trades.
        """
        return np.max(self.positive_profit)

    @property
    def largest_profit_date(self):
        """Returns the date of the largest winning trade."""
        return self.exit_time[np.where(self.profit == self.largest_profit)[0][0]]

    @property
    def largest_loss(self) -> float:
        """Returns the largest loss of all trades."""
        return np.min(self.negative_profit)

    @property
    def largest_loss_date(self):
        """Return the date of the largest loosing trade."""
        return self.exit_time[np.where(self.profit == self.largest_loss)[0][0]]

    @property
    def number_of_trades(self):
        return len(self.profit)

    @property
    def number_of_losses(self):
        """Returns the number of loosing trades, (profit < 0)."""
        return len(self.negative_profit)

    @property
    def number_of_wins(self):
        """Returns the number of winning trades, (profit > 0)."""
        return len(self.positive_profit)

    @property
    def sum_profit(self):
        """Returns the sum of all the profitable trades."""
        return sum(self.positive_profit)

    @property
    def sum_loss(self):
        """Returns the sum of all the loosing trades."""
        return sum(self.negative_profit)

    @property
    def sum_profit_and_loss(self):
        """Returns the sum of all the trades."""
        return sum(self.profit)

    @property
    def profit_factor(self):
        """
        Strategy is considered good if the return value is > 1.
            - If it is greater than 1: The expected return of a trade is positive.
            - If it is less than 1: The expected return of a trade is negative.

        Calculation formula:
            - (Win rate * Average of winning trades) / (Loss rate * Average of loosing trades)
        :return:
        """
        return (self.win_rate * self.average_profit) / (self.loss_rate * abs(self.average_loss))

    @property
    def expectancy(self):
        """
        The expected return of each trade.

        Calculation formula:
            - (Win rate * Average of winning trades) – (Loss rate * Average of loosing trades)

        Note: Same as self.average_profit_and_loss
        """
        return (self.win_rate * self.average_profit) - (self.loss_rate * abs(self.average_loss))

    @property
    def average_profit(self):
        """Sum of the profitable trades / number of winning trades."""
        return self.sum_profit / self.number_of_wins

    @property
    def average_loss(self):
        """Sum of the loosing trades / number of loosing trades."""
        return self.sum_loss / self.number_of_losses

    @property
    def average_profit_and_loss(self):
        """
        Sum of all trades / number of trades.

        Calculation formula:
            - Sum P&L / Number of trades

        Note: Same as self.expectancy
        """
        return self.sum_profit_and_loss / self.number_of_trades
