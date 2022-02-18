import copy
from typing import Callable, Optional, Union, List

from trader.core.model import Candles
from trader.core.exception import PositionError, BalanceError
from trader.core.enum import OrderSide
from trader.core.enum.position_status import PositionStatus
from trader.core.interface import FuturesTrader
from trader.core.util.trade import create_orders
from trader.core.util.common import remove_none

from .balance import BacktestBalance
from .exception import NotEnoughFundsError
from .order_group import BacktestOrderGroup
from .position import BacktestPosition


class BacktestFuturesTrader(FuturesTrader, Callable):

    def __init__(
            self,
            balance=BacktestBalance(asset="USD", amount=1_000),
            maker_fee_rate=0.0,
            taker_fee_rate=0.0,
    ):
        """
        Maker fee is applied if the order goes into the order book (e.g. limit order)
        Taker fee is applied if the order fills immediately (e.g. market order)
        """
        super().__init__()

        self.start_balance = copy.deepcopy(balance)
        self.balance = balance

        self.maker_fee_rate = maker_fee_rate
        self.taker_fee_rate = taker_fee_rate

        self.positions: List[BacktestPosition] = list()

        self.order_group: Optional[BacktestOrderGroup] = None
        self._leverage: Optional[int] = None
        self.__candles: Optional[Candles] = None

    def __call__(self, candles: Candles):
        self.__candles = candles
        if self.order_group is not None:
            self.order_group(
                candles=candles,
                leverage=self._leverage,
                balance=self.balance,
                maker_fee_rate=self.maker_fee_rate,
                taker_fee_rate=self.taker_fee_rate,
            )
            if self.order_group.status == PositionStatus.CLOSED:
                self.positions.append(self.order_group.position)
                self.order_group = None

    def get_latest_price(self, symbol: str):
        return self.__candles.latest_close_price

    def _cancel_orders(self, symbol: str):
        if self.order_group is None:
            return []

        orders = remove_none((
            self.order_group.entry_order,
            self.order_group.close_order,
            self.order_group.stop_order,
            self.order_group.take_profit_order,
        ))
        self.order_group.cancel_orders()
        return orders

    def _create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ):
        self._leverage = leverage

        if money > self.balance.free:
            raise NotEnoughFundsError(
                f"You tried to enter a position with {money} {self.balance.asset}, "
                f"while your balance is only {self.balance}."
            )

        if self.__is_in_position():
            raise PositionError(
                f"Creating a {symbol} position is not allowed, because a {symbol} position is already opened."
            )

        orders = create_orders(
            symbol=symbol,
            money=money,
            side=side,
            entry_price=price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
        )
        self.order_group = BacktestOrderGroup(*orders)
        return remove_none(orders)

    def __is_in_position(self):
        return self.order_group is not None and self.order_group.is_in_position()

    def _close_position_market(self, symbol: str):
        if not self.__is_in_position():
            raise PositionError("No position to close.")

        self.order_group.create_close_order()
        return self.order_group.close_order

    def _close_position_limit(self, symbol: str, price: float):
        if not self.__is_in_position():
            raise PositionError("No position to close.")

        self.order_group.create_close_order(price=price)
        return self.order_group.close_order

    def _get_balance(self, asset: str):
        if asset == self.balance.asset:
            return self.balance
        raise BalanceError(f"{asset} balance not found!")

    def _get_open_orders(self, symbol: str):
        if self.order_group is None:
            return []

        return remove_none((
            self.order_group.entry_order,
            self.order_group.close_order,
            self.order_group.stop_order,
            self.order_group.take_profit_order,
        ))

    def _get_position(self, symbol: str):
        if self.__is_in_position():
            return self.order_group.position

    def _set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage
