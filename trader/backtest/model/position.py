from __future__ import annotations

from trader.core.enumerate import OrderSide, OrderType
from trader.core.exception import LiquidationError
from trader.core.model import Position
from trader.core.const.trade_actions import LONG
from trader.core.util.trade import calculate_profit


class BacktestPosition(Position):

    __slots__ = "__profit"

    def __init__(
            self,
            symbol: str,
            entry_order_type: str | OrderType,
            entry_time: int,
            entry_price: float,
            entry_fee: float,
            side: int | OrderSide,
            money: float,
            quantity: float,
            leverage: int,
    ):
        super().__init__(
            symbol=symbol,
            money=money,
            side=side,
            leverage=leverage,
            quantity=quantity,
            entry_order_type=entry_order_type,
            entry_time=entry_time,
            entry_price=entry_price,
            entry_fee=entry_fee,
        )
        self.__profit = .0

    def liquidation_check(self, low_price: float, high_price: float, balance: float):
        """
        Checks if position got liquidated while it is open.

        :param low_price: Latest low price.
        :param high_price: Latest high price.
        :param balance: Available account balance.
        :raises LiquidationError: If position loss is greater than the available balance.
        """
        if self.is_closed():
            return

        possible_liquidation_price = low_price if self.side == LONG else high_price

        lowest_profit = self.__calculate_profit(possible_liquidation_price)
        is_liquidated = lowest_profit < 0 and abs(lowest_profit) >= balance
        if is_liquidated:
            raise LiquidationError(
                f"Position liquidated! "
                f"Your remaining balance ({balance}) couldn't cover your position."
            )

    def update(self, latest_price: float):
        """Updates profit based on `latest_price`."""
        self.__profit = self.__calculate_profit(self.exit_price if self.is_closed() else latest_price)

    def close(self, time: int, price: float, fee: float):
        super(BacktestPosition, self).close(time=time, price=price, fee=fee)
        self.update(price)

    @property
    def profit(self):
        """
        Returns current profit of this position.

        :examples:
        >>> from trader.backtest.model import BacktestPosition
        >>> from trader.core.enumerate import OrderSide

        >>> position = BacktestPosition(
        ... symbol='EXAMPLE',
        ... money=100.0,
        ... side=OrderSide.LONG,
        ... leverage=1,
        ... quantity=1,
        ... entry_time=1640991600,
        ... entry_price=100,
        ... entry_fee=0.0)

        >>> position.profit == 0.0
        True

        >>> position.update(200)
        >>> position.profit == 100.0
        True

        >>> position.close(time=1643670000, price=150, fee=0.0)
        >>> position.profit == 50.0
        True
        """
        return self.__profit

    def __calculate_profit(self, price: float):
        return calculate_profit(
            side=self.side,
            entry_price=self.entry_price,
            exit_price=price,
            quantity=self.quantity,
            leverage=self.leverage,
        )
