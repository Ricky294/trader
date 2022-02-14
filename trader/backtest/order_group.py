from typing import Optional, Union

from trader.core.exception import PositionError
from trader.core.enum import PositionStatus
from trader.core.model import MarketOrder, StopMarketOrder, TakeProfitMarketOrder, LimitOrder, Candles
from trader.core.util.trade import opposite_side

from .balance import BacktestBalance
from .position import BacktestPosition
from .util import is_order_filled, get_filled_first


class BacktestOrderGroup:

    __slots__ = (
        "status",
        "entry_order",
        "stop_order",
        "take_profit_order",
        "exit_order",
        "position",
    )

    def __init__(
            self,
            entry_order: Union[MarketOrder, LimitOrder],
            stop_order: StopMarketOrder = None,
            take_profit_order: TakeProfitMarketOrder = None,
    ):
        self.status = PositionStatus.NONE
        self.entry_order = entry_order
        self.stop_order = stop_order
        self.take_profit_order = take_profit_order
        self.position: Optional[BacktestPosition] = None
        self.exit_order: Optional[Union[MarketOrder, LimitOrder]] = None

    def __call__(
            self,
            candles: Candles,
            leverage: int,
            balance: BacktestBalance,
            maker_fee_rate: float,
            taker_fee_rate: float,
    ):
        if self.status == PositionStatus.NONE:
            self._entry_logic(
                candles=candles,
                balance=balance,
                leverage=leverage,
                maker_fee_rate=maker_fee_rate,
                taker_fee_rate=taker_fee_rate,
            )

        elif self.status == PositionStatus.OPEN:
            self.position(balance=balance, candles=candles)
            self._exit_logic(
                balance=balance,
                candles=candles,
                leverage=leverage,
                maker_fee_rate=maker_fee_rate,
                taker_fee_rate=taker_fee_rate,
            )

    def _entry_logic(
            self,
            candles: Candles,
            balance: BacktestBalance,
            leverage: int,
            maker_fee_rate: float,
            taker_fee_rate: float,
    ):
        if is_order_filled(high_price=candles.latest_high_price, low_price=candles.latest_low_price, order=self.entry_order):
            self.position = BacktestPosition(
                self.entry_order,
                balance=balance,
                maker_fee_rate=maker_fee_rate,
                taker_fee_rate=taker_fee_rate,
                candles=candles,
                leverage=leverage,
            )
            self.status = PositionStatus.OPEN

    def _exit_logic(
            self,
            candles: Candles,
            balance: BacktestBalance,
            leverage: int,
            maker_fee_rate: float,
            taker_fee_rate: float,
    ):
        filled_order = get_filled_first(
            high_price=candles.latest_high_price,
            low_price=candles.latest_low_price,
            open_price=candles.latest_open_price,
            take_profit_order=self.take_profit_order,
            stop_order=self.stop_order,
            exit_order=self.exit_order,
        )

        if filled_order is not None:
            if filled_order.stop_price is not None:
                price = filled_order.stop_price
            elif filled_order.price is not None:
                price = filled_order.price
            else:
                price = candles.latest_close_price

            self.position.close(
                time=int(candles.latest_open_time),
                price=price,
                balance=balance,
                order=filled_order,
                taker_fee_rate=taker_fee_rate,
                maker_fee_rate=maker_fee_rate,
                leverage=leverage,
            )

            self.status = PositionStatus.CLOSED

    def create_close_order(self, price: float = None):
        if self.status != PositionStatus.OPEN:
            raise PositionError("Can't create a position closing order because there isn't any open position!")

        self.exit_order = (
            MarketOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money(),
            )
            if price is None
            else LimitOrder(
                symbol=self.position.symbol,
                side=opposite_side(self.position.side),
                money=self.position.money(),
                price=price,
            )
        )

    def cancel_stop_order(self):
        self.stop_order = None

    def cancel_take_profit_order(self):
        self.take_profit_order = None

    def cancel_close_order(self):
        self.exit_order = None

    def cancel_orders(self):
        self.entry_order = None
        self.exit_order = None
        self.stop_order = None
        self.take_profit_order = None

    def is_in_position(self):
        return self.status == PositionStatus.OPEN
