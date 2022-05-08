from __future__ import annotations

from trader.core.enumerate import OrderSide
from trader.core.exception import LiquidationError
from trader.core.model import Position
from trader.core.const.trade_actions import LONG
from trader.core.util.trade import position_profit


class BacktestPosition(Position):

    __slots__ = "__profit"

    def __init__(
            self,
            symbol: str,
            money: float,
            side: int | OrderSide,
            leverage: int,
            entry_time: int,
            entry_price: float,
            entry_fee: float,
    ):
        super().__init__(symbol, money, side, leverage, entry_time, entry_price, entry_fee)
        self.__profit = .0

    def liquidation_check(self, low_price: float, high_price: float, balance: float):
        """
        Checks if position got liquidated while it is open.

        :param low_price: Latest low price.
        :param high_price: Latest high price.
        :param balance: Available account balance.
        :raises LiquidationError: If position loss is greater than the available balance.
        """
        if self.is_closed:
            return

        possible_liquidation_price = low_price if self.side == LONG else high_price

        lowest_profit = self.__calculate_profit(possible_liquidation_price)
        is_liquidated = lowest_profit < 0 and abs(lowest_profit) >= balance
        if is_liquidated:
            raise LiquidationError(
                f"Position liquidated! "
                f"Your remaining balance ({balance}) couldn't cover your position."
            )

    def update_profit(self, close_price: float):
        """Calculates and stores current profit based on `close_price`"""
        self.__profit = self.__calculate_profit(self.exit_price if self.is_closed else close_price)

    def set_exit(self, time: int, price: float, fee: float):
        super(BacktestPosition, self).set_exit(time=time, price=price, fee=fee)
        self.update_profit(price)

    @property
    def profit(self):
        return self.__profit

    def __calculate_profit(self, price: float):
        return position_profit(
            side=self.side,
            entry_price=self.entry_price,
            exit_price=price,
            quantity=self.quantity,
            leverage=self.leverage,
        )
