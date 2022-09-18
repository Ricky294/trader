from __future__ import annotations

from datetime import datetime

from trader.core.const import Side, OrderType
from trader.core.exception import SideError
from trader.core.model import Order
from trader.settings import Settings


def check_trailing_percentage(trailing_percentage: float):
    if trailing_percentage > Settings.trailing_rate_max_percentage:
        raise ValueError(
            f'Trying to set maximum trailing rate percentage to {trailing_percentage} '
            f'but the allowed maximum is {Settings.trailing_rate_max_percentage}.'
        )
    elif trailing_percentage < Settings.trailing_rate_step_size:
        raise ValueError(
            f'Trying to set trailing to {trailing_percentage} '
            f'which is below the minimum {Settings.trailing_rate_step_size}.'
        )


def check_order_side(side: Side, activation_price: float, current_price: float):
    if activation_price is not None:
        if activation_price < current_price and side is Side.SELL:
            raise SideError(
                f'Invalid order side {side}.'
                f'Side must be {side.opposite()} if activation price is less than current price.'
            )
        elif activation_price > current_price and side is Side.BUY:
            raise SideError(
                f'Invalid order side {side}.'
                f'Side must be {side.opposite()} if activation price is greater than current price.'
            )


def update(self):

    def wrapper(high_price: float, low_price: float):
        def update_stop_price():
            if self.side is Side.BUY:  # position.side - SHORT
                new_stop = low_price * (1 + self.trailing_percentage)
                if new_stop < self.stop_price:
                    self.stop_price = new_stop
            else:  # position.side - LONG
                new_stop = high_price * (1 - self.trailing_percentage)
                if new_stop > self.stop_price:
                    self.stop_price = new_stop

        if not self.is_active:
            if (
                    # A buy trailing stop order will be placed if activation price >= low price
                    self.side is Side.BUY and self.activation_price >= low_price
                    # A sell trailing stop order will be placed if activation price <= high price
                    or self.side is Side.SELL and self.activation_price <= high_price
            ):
                self.is_active = True

        if self.is_active and not self.is_stopped:
            if (
                    self.side is Side.BUY and high_price >= self.stop_price  # position.side = SHORT
                    or self.side is Side.SELL and low_price <= self.stop_price  # position.side = LONG
            ):
                self.is_stopped = True
            else:
                update_stop_price()

    return wrapper


class BacktestTrailingStopMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Side,
            trailing_percentage: float,
            current_price: float,
            amount: float,
            quantity: float,
            order_id=None,
            time: datetime | int = None,
            activation_price: float = None,
            reduce_only=True,
    ):
        if trailing_percentage > Settings.trailing_rate_max_percentage:
            raise ValueError(
                f'Trying to set maximum trailing rate percentage to {trailing_percentage} '
                f'but the allowed maximum is {Settings.trailing_rate_max_percentage}.'
            )
        elif trailing_percentage < Settings.trailing_rate_step_size:
            raise ValueError(
                f'Trying to set trailing to {trailing_percentage} '
                f'which is below the minimum {Settings.trailing_rate_step_size}.'
            )

        if activation_price is not None:
            if activation_price < current_price and side is Side.SELL:
                raise SideError(
                    f'Invalid order side {side}.'
                    f'Side must be {side.opposite()} if activation price is less than current price.'
                )
            elif activation_price > current_price and side is Side.BUY:
                raise SideError(
                    f'Invalid order side {side}.'
                    f'Side must be {side.opposite()} if activation price is greater than current price.'
                )

        act_price = current_price if activation_price is None else activation_price
        super().__init__(
            type=OrderType.TRAILING_STOP_MARKET,
            order_id=order_id,
            time=time,
            symbol=symbol,
            side=side,
            amount=amount,
            quantity=quantity,
            trailing_percentage=trailing_percentage,
            activation_price=act_price,
            stop_price=act_price * (1 + trailing_percentage / 100) if side is Side.BUY else act_price * (1 - trailing_percentage / 100),
            reduce_only=reduce_only
        )
        self.is_active = False if activation_price else True
        self.is_stopped = False

    def update_stop_price(self, high_price: float, low_price: float):
        if self.side is Side.BUY:   # position.side - SHORT
            new_stop = low_price * (1 + self.trailing_percentage)
            if new_stop < self.stop_price:
                self. stop_price = new_stop
        else:  # position.side - LONG
            new_stop = high_price * (1 - self.trailing_percentage)
            if new_stop > self.stop_price:
                self.stop_price = new_stop

    def __call__(self, high_price: float, low_price: float):
        if not self.is_active:
            if (
                    # A buy trailing stop order will be placed if activation price >= low price
                    self.side is Side.BUY and self.activation_price >= low_price
                    # A sell trailing stop order will be placed if activation price <= high price
                    or self.side is Side.SELL and self.activation_price <= high_price
            ):
                self.is_active = True

        if self.is_active and not self.is_stopped:
            if (
                    self.side is Side.BUY and high_price >= self.stop_price   # position.side = SHORT
                    or self.side is Side.SELL and low_price <= self.stop_price   # position.side = LONG
            ):
                self.is_stopped = True
            else:
                self.update_stop_price(high_price=high_price, low_price=low_price)
