import copy
from typing import Callable, Optional, Union, List

from .balance import BacktestBalance
from trader.core.model import Candles
from trader.core import PositionError
from .exceptions import NotEnoughFundsError
from .order_group import BacktestOrderGroup
from .position import BacktestPosition
from ..core.enum import OrderSide
from ..core.enum.position_status import PositionStatus
from ..core.interface import FuturesTrader
from ..core.util.trade import create_orders


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

    def get_order(self):
        return self.order_group.entry_order

    def get_take_profit_order(self):
        return self.order_group.take_profit_order

    def get_stop_loss_order(self):
        return self.order_group.stop_order

    def cancel_orders(self, symbol: str):
        self.order_group.cancel_orders()

    def cancel_take_profit_order(self, symbol: str):
        self.order_group.take_profit_order = None

    def cancel_stop_loss_orders(self, symbol: str):
        self.order_group.stop_order = None

    def create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            entry_price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ):
        self._leverage = leverage

        if money > self.balance.free:
            raise NotEnoughFundsError(
                f"You tried to enter a position with {money} {self.balance.asset}, "
                f"while your balance is only {self.balance}."
            )

        if self.order_group is None or not self.order_group.is_in_position():
            self.order_group = BacktestOrderGroup(
                *create_orders(
                    symbol=symbol,
                    money=money,
                    side=side,
                    entry_price=entry_price,
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price,
                )
            )

    def close_position_market(self, symbol: str):
        if not self.order_group.is_in_position():
            raise PositionError("No position to close.")

        self.order_group.create_close_order()

    def close_position_limit(self, symbol: str, price: float):
        if not self.order_group.is_in_position():
            raise PositionError("No position to close.")

        self.order_group.create_close_order(price=price)

    def get_balance(self, asset: str) -> BacktestBalance:
        return self.balance

    def get_open_orders(self, symbol: str):
        if self.order_group is None:
            return []

        open_orders = []
        if self.order_group.entry_order is not None:
            open_orders.append(self.order_group.entry_order)
        elif self.order_group.take_profit_order is not None:
            open_orders.append(self.order_group.take_profit_order)
        elif self.order_group.stop_order is not None:
            open_orders.append(self.order_group.stop_order)
        return open_orders

    def get_position(self, symbol: str) -> Optional[BacktestPosition]:
        if self.order_group is not None:
            return self.order_group.position

    def set_leverage(self, symbol: str, leverage: int):
        self._leverage = leverage

    def get_leverage(self, symbol) -> int:
        return self._leverage
