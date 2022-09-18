import numpy as np

from trader.core.const import Side
from trader.core.model import Position
from trader.data.model import Models


class Positions(Models[Position]):

    # Symbol
    @property
    def symbol(self):
        return np.array(tuple(pos.symbol for pos in self))

    # Side
    @property
    def side(self):
        return np.array(tuple(pos.side for pos in self))

    @property
    def entry_side(self):
        return np.array(tuple(pos.side for pos in self if pos.is_entry))

    @property
    def adjust_side(self):
        return np.array(tuple(pos.side for pos in self if pos.is_adjust))

    @property
    def close_side(self):
        return np.array(tuple(pos.side for pos in self if pos.is_close))

    # Amount
    @property
    def amount(self):
        return np.array(tuple(pos.amount for pos in self))

    @property
    def entry_amount(self):
        return np.array(tuple(pos.amount for pos in self if pos.is_entry))

    @property
    def adjust_amount(self):
        return np.array(tuple(pos.amount for pos in self if pos.is_adjust))

    @property
    def close_amount(self):
        return np.array(tuple(pos.amount for pos in self if pos.is_close))

    @property
    def long_entry_amount(self):
        return self.entry_amount[self.entry_side == Side.LONG]

    @property
    def long_adjust_amount(self):
        return self.adjust_amount[self.adjust_side == Side.LONG]

    @property
    def long_close_amount(self):
        return self.close_amount[self.close_side == Side.LONG]

    @property
    def short_entry_amount(self):
        return self.entry_amount[self.entry_side == Side.SHORT]

    @property
    def short_adjust_amount(self):
        return self.adjust_amount[self.adjust_side == Side.SHORT]

    @property
    def short_close_amount(self):
        return self.close_amount[self.close_side == Side.SHORT]

    # Quantity
    @property
    def quantity(self):
        return np.array(tuple(pos.quantity for pos in self))

    @property
    def entry_quantity(self):
        return np.array(tuple(pos.quantity for pos in self if pos.is_entry))

    @property
    def adjust_quantity(self):
        return np.array(tuple(pos.quantity for pos in self if pos.is_adjust))

    @property
    def close_quantity(self):
        return np.array(tuple(pos.quantity for pos in self if pos.is_close))

    @property
    def long_entry_quantity(self):
        return self.entry_quantity[self.entry_side == Side.LONG]

    @property
    def long_adjust_quantity(self):
        return self.adjust_quantity[self.adjust_side == Side.LONG]

    @property
    def long_close_quantity(self):
        return self.close_quantity[self.close_side == Side.LONG]

    @property
    def short_entry_quantity(self):
        return self.entry_quantity[self.entry_side == Side.SHORT]

    @property
    def short_adjust_quantity(self):
        return self.adjust_quantity[self.adjust_side == Side.SHORT]

    @property
    def short_close_quantity(self):
        return self.close_quantity[self.close_side == Side.SHORT]

    # Price
    @property
    def price(self):
        return np.array(tuple(pos.price for pos in self))

    @property
    def entry_price(self):
        return np.array(tuple(pos.price for pos in self if pos.is_entry))

    @property
    def adjust_price(self):
        return np.array(tuple(pos.price for pos in self if pos.is_adjust))

    @property
    def close_price(self):
        return np.array(tuple(pos.price for pos in self if pos.is_close))

    @property
    def long_entry_price(self):
        return self.entry_price[self.entry_side == Side.LONG]

    @property
    def long_adjust_price(self):
        return self.adjust_price[self.adjust_side == Side.LONG]

    @property
    def long_close_price(self):
        return self.close_price[self.close_side == Side.LONG]

    @property
    def short_entry_price(self):
        return self.entry_price[self.entry_side == Side.SHORT]

    @property
    def short_adjust_price(self):
        return self.adjust_price[self.adjust_side == Side.SHORT]

    @property
    def short_close_price(self):
        return self.close_price[self.close_side == Side.SHORT]

    # Fee
    @property
    def fee(self):
        return np.array(tuple(pos.fee for pos in self))

    @property
    def entry_fee(self):
        return np.array(tuple(pos.fee for pos in self if pos.is_entry))

    @property
    def adjust_fee(self):
        return np.array(tuple(pos.fee for pos in self if pos.is_adjust))

    @property
    def close_fee(self):
        return np.array(tuple(pos.fee for pos in self if pos.is_close))

    @property
    def long_entry_fee(self):
        return self.entry_fee[self.entry_side == Side.LONG]

    @property
    def long_adjust_fee(self):
        return self.adjust_fee[self.adjust_side == Side.LONG]

    @property
    def long_close_fee(self):
        return self.close_fee[self.close_side == Side.LONG]

    @property
    def short_entry_fee(self):
        return self.entry_fee[self.entry_side == Side.SHORT]

    @property
    def short_adjust_fee(self):
        return self.adjust_fee[self.adjust_side == Side.SHORT]

    @property
    def short_close_fee(self):
        return self.close_fee[self.close_side == Side.SHORT]

    # Leverage
    @property
    def leverage(self):
        return np.array(tuple(pos.leverage for pos in self))

    @property
    def entry_leverage(self):
        return np.array(tuple(pos.leverage for pos in self if pos.is_entry))

    @property
    def adjust_leverage(self):
        return np.array(tuple(pos.leverage for pos in self if pos.is_adjust))

    @property
    def close_leverage(self):
        return np.array(tuple(pos.leverage for pos in self if pos.is_close))

    @property
    def long_entry_leverage(self):
        return self.entry_leverage[self.entry_side == Side.LONG]

    @property
    def long_adjust_leverage(self):
        return self.adjust_leverage[self.adjust_side == Side.LONG]

    @property
    def long_close_leverage(self):
        return self.close_leverage[self.close_side == Side.LONG]

    @property
    def short_entry_leverage(self):
        return self.entry_leverage[self.entry_side == Side.SHORT]

    @property
    def short_adjust_leverage(self):
        return self.adjust_leverage[self.adjust_side == Side.SHORT]

    @property
    def short_close_leverage(self):
        return self.close_leverage[self.close_side == Side.SHORT]

    # Datetime
    @property
    def entry_time(self):
        return np.array(tuple(pos.create_time for pos in self if pos.is_entry))

    @property
    def adjust_time(self):
        return np.array(tuple(pos.create_time for pos in self if pos.is_adjust))

    @property
    def close_time(self):
        return np.array(tuple(pos.create_time for pos in self if pos.is_close))

    @property
    def long_entry_time(self):
        return self.entry_time[self.entry_side == Side.LONG]

    @property
    def long_adjust_time(self):
        return self.adjust_time[self.adjust_side == Side.LONG]

    @property
    def long_close_time(self):
        return self.close_time[self.close_side == Side.LONG]

    @property
    def short_entry_time(self):
        return self.entry_time[self.entry_side == Side.SHORT]

    @property
    def short_adjust_time(self):
        return self.adjust_time[self.adjust_side == Side.SHORT]

    @property
    def short_close_time(self):
        return self.close_time[self.close_side == Side.SHORT]

    @property
    def positive_close_profit_time(self):
        return self.close_time[self.close_profit >= 0]

    @property
    def zero_close_profit_time(self):
        return self.close_time[self.close_profit == 0]

    @property
    def negative_close_profit_time(self):
        return self.close_time[self.close_profit < 0]

    # Timestamp
    @property
    def entry_timestamp(self):
        return np.array(tuple(pos.create_timestamp for pos in self if pos.is_entry))

    @property
    def adjust_timestamp(self):
        return np.array(tuple(pos.create_timestamp for pos in self if pos.is_adjust))

    @property
    def close_timestamp(self):
        return np.array(tuple(pos.create_timestamp for pos in self if pos.is_close))

    @property
    def long_entry_timestamp(self):
        return self.entry_timestamp[self.entry_side == Side.LONG]

    @property
    def long_adjust_timestamp(self):
        return self.adjust_timestamp[self.adjust_side == Side.LONG]

    @property
    def long_close_timestamp(self):
        return self.close_timestamp[self.close_side == Side.LONG]

    @property
    def short_entry_timestamp(self):
        return self.entry_timestamp[self.entry_side == Side.SHORT]

    @property
    def short_adjust_timestamp(self):
        return self.adjust_timestamp[self.adjust_side == Side.SHORT]

    @property
    def short_close_timestamp(self):
        return self.close_timestamp[self.close_side == Side.SHORT]

    @property
    def positive_close_profit_timestamp(self):
        return self.close_timestamp[self.close_profit >= 0]

    @property
    def zero_close_profit_timestamp(self):
        return self.close_timestamp[self.close_profit == 0]

    @property
    def negative_close_profit_timestamp(self):
        return self.close_timestamp[self.close_profit < 0]

    # Profit
    @property
    def profit(self):
        return np.array(tuple(pos.profit for pos in self))

    @property
    def entry_profit(self):
        return np.array(tuple(pos.profit for pos in self if pos.is_entry))

    @property
    def adjust_profit(self):
        return np.array(tuple(pos.profit for pos in self if pos.is_adjust))

    @property
    def close_profit(self):
        return np.array(tuple(pos.profit for pos in self if pos.is_close))

    @property
    def long_entry_profit(self):
        return self.close_profit[self.entry_side == Side.LONG]

    @property
    def long_adjust_profit(self):
        return self.adjust_profit[self.adjust_side == Side.LONG]

    @property
    def long_close_profit(self):
        return self.close_profit[self.close_side == Side.LONG]

    @property
    def short_entry_profit(self):
        return self.entry_profit[self.entry_side == Side.SHORT]

    @property
    def short_adjust_profit(self):
        return self.adjust_profit[self.adjust_side == Side.SHORT]

    @property
    def short_close_profit(self):
        return self.close_profit[self.close_side == Side.SHORT]

    @property
    def positive_close_profit(self):
        return self.close_profit[self.close_profit > 0]

    @property
    def zero_close_profit(self):
        return self.close_profit[self.close_profit == 0]

    @property
    def negative_close_profit(self):
        return self.close_profit[self.close_profit < 0]

    # Stats
    @property
    def win_rate(self):
        """
        Number of winning trades / number of trades

        :return: float between 0 and 1
        """
        try:
            return self.number_of_wins / self.number_of_closed_positions
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
            return self.number_of_losses / self.number_of_closed_positions
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
        try:
            return np.max(self.positive_close_profit)
        except ValueError:
            return .0

    @property
    def largest_profit_date(self):
        """Returns the date of the largest winning trade."""
        try:
            return self.close_timestamp[np.where(self.profit == self.largest_profit)[0][0]]
        except IndexError:
            return None

    @property
    def largest_loss(self):
        """Returns the largest loss of all trades."""
        try:
            return np.min(self.negative_close_profit)
        except ValueError:
            return .0

    @property
    def largest_loss_date(self) -> int | None:
        """Return the date of the largest loosing trade."""
        try:
            return self.close_timestamp[np.where(self.profit == self.largest_loss)[0][0]]
        except IndexError:
            return None

    @property
    def number_of_opened_positions(self):
        return len(self.entry_time)

    @property
    def number_of_closed_positions(self):
        return len(self.close_time)

    @property
    def number_of_losses(self):
        """Returns the number of loosing trades, (profit < 0)."""
        return len(self.negative_close_profit)

    @property
    def number_of_wins(self):
        """Returns the number of winning trades, (profit > 0)."""
        return len(self.positive_close_profit)

    @property
    def sum_profit(self):
        """Returns the sum of all the profitable trades."""
        return sum(self.positive_close_profit)

    @property
    def sum_loss(self):
        """Returns the sum of all the loosing trades."""
        return sum(self.negative_close_profit)

    @property
    def sum_profit_and_loss(self):
        """Returns the sum of closed position profits."""
        return sum(self.close_profit)

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
        try:
            return (self.win_rate*self.average_profit) / (self.loss_rate*abs(self.average_loss))
        except ZeroDivisionError:
            return .0

    @property
    def expectancy(self):
        """
        The expected return of each trade.

        Calculation formula:
            - (Win rate * Average of winning trades) – (Loss rate * Average of loosing trades)

        Note: Same as self.average_profit_and_loss
        """
        return self.win_rate*self.average_profit - self.loss_rate*abs(self.average_loss)

    @property
    def average_profit(self):
        """Sum of the profitable trades / number of winning trades."""
        try:
            return self.sum_profit / self.number_of_wins
        except ZeroDivisionError:
            return .0

    @property
    def average_loss(self):
        """Sum of the loosing trades / number of loosing trades."""
        try:
            return self.sum_loss / self.number_of_losses
        except ZeroDivisionError:
            return .0

    @property
    def average_profit_and_loss(self):
        """
        Sum of all trades / number of trades.

        Calculation formula:
            - Sum P&L / Number of trades

        Note: Same as self.expectancy
        """
        try:
            return self.sum_profit_and_loss / self.number_of_closed_positions
        except ZeroDivisionError:
            return .0
