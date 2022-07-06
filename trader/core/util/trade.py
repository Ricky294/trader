"""Implements core trading utility functions.

Functions:
    * side_to_int - Converts parameter `side` to its int representation.
    * side_to_buy_sell - Converts parameter `side` to str 'BUY' or 'SELL'.
    * side_to_long_short - Converts parameter `side` to str 'LONG' or 'SHORT'.
    * opposite_side - Converts parameter `side` to its opposite (e.g. BUY --> SELL).
    * create_orders - Creates Order objects based on the parameters.
"""

from __future__ import annotations

import datetime
from typing import Iterable, Callable

import pandas as pd

import trader.core.util.format as fmt
from trader.core.const.trade_actions import BUY, SELL, LONG, SHORT
from trader.core.enumerate import OrderSide, TimeFormat
from trader.core.enumerate.precision_format import PrecisionFormat
from trader.core.enumerate.side_format import SideFormat
from trader.core.exception import BalanceError, LeverageError
from trader.data.typing import Side


def side_to_int(side: Side):
    """
    Converts `side` to int

    :examples:
    >>> side_to_int(BUY) == BUY == LONG
    True

    >>> side_to_int('LONG') == BUY == LONG
    True

    >>> side_to_int('SHORT') == SELL == SHORT
    True

    >>> side_to_int(OrderSide.SELL) == SELL == SHORT
    True
    """

    if isinstance(side, int):
        if side in (BUY, SELL):
            return side
        raise ValueError(f'Param `side` (type: int) must be {BUY} or {SELL}')

    elif isinstance(side, str):
        if side.upper() in ('BUY', 'LONG'):
            return BUY
        elif side.upper() in ('SELL', 'SHORT'):
            return SELL
        raise ValueError('Param `side` (type: str) must be BUY, SELL, LONG or SHORT.')

    elif isinstance(side, OrderSide):
        return int(side)

    raise ValueError(f'Unsupported type for side: {type(side)}')


def side_to_buy_sell(side: Side):
    """
    Converts parameter to 'BUY' or 'SELL' (str).

    :examples:
    >>> side_to_buy_sell('SHORT')
    'SELL'

    >>> side_to_buy_sell(BUY)
    'BUY'

    >>> side_to_buy_sell(OrderSide.LONG)
    'BUY'

    :return: str ('BUY' | 'SELL')
    :raises ValueError: If param side is invalid.
    """

    if isinstance(side, str):
        if side.upper() in ('SHORT', 'SELL'):
            return 'SELL'
        elif side.upper() in ('LONG', 'BUY'):
            return 'BUY'
        else:
            raise ValueError(f'Invalid side value: {side!r}')

    side = int(side)
    if side == BUY:
        return 'BUY'
    elif side == SELL:
        return 'SELL'
    raise ValueError(f'Side must be {BUY!r} or {SELL!r}.')


def side_to_long_short(side: Side):
    """
    Converts parameter to 'LONG' or 'SHORT' (str).

    :examples:
    >>> side_to_long_short('SELL')
    'SHORT'

    >>> side_to_long_short(LONG)
    'LONG'

    >>> side_to_long_short(OrderSide.BUY)
    'LONG'

    :return: str ('LONG' | 'SHORT')
    :raises ValueError: If param side is invalid.
    """
    if isinstance(side, str):
        if side.upper() in ('SHORT', 'SELL'):
            return 'SHORT'
        elif side.upper() in ('LONG', 'BUY'):
            return 'LONG'
        else:
            raise ValueError(f'Invalid side value: {side!r}')

    side = int(side)
    if side == BUY:
        return 'LONG'
    elif side == SELL:
        return 'SHORT'
    raise ValueError(f'Side must be {LONG!r} or {SHORT!r}.')


def format_side(side: Side | Iterable[Side], side_format: SideFormat):
    """
    Formats `side` value(s) based on `side_format`.

    :param side: Timestamp in seconds (single value or iterable)
    :param side_format: Applied conversion on time parameter

    :examples:
    >>> format_side(0, SideFormat.BUY_SELL)
    'BUY'

    >>> format_side(1, SideFormat.LONG_SHORT)
    'SHORT'

    >>> format_side([0, 1], SideFormat.LONG_SHORT)
    ['LONG', 'SHORT']
    """
    def convert(func: Callable, *args, **kwargs):
        if isinstance(side, Iterable):
            return [func(t, *args, **kwargs) for t in side]
        return func(side, *args, **kwargs)

    if side_format == SideFormat.NUM:
        return convert(side_to_int)
    elif side_format == SideFormat.BUY_SELL:
        return convert(side_to_buy_sell)
    return convert(side_to_long_short)


def format_time(time: int | Iterable[int], time_format: TimeFormat):
    """
    Formats `time` value(s) based on `time_format`.

    :param time: Timestamp in seconds (single value or iterable)
    :param time_format: Applied conversion on time parameter

    :examples:
    >>> format_time(1640995200, TimeFormat.DATETIME)
    datetime.datetime(2022, 1, 1, 1, 0)

    >>> format_time(1640995200, TimeFormat.PANDAS)
    Timestamp('2022-01-01 00:00:00')

    >>> format_time([1640995200, 1641081600], TimeFormat.PANDAS)
    [Timestamp('2022-01-01 00:00:00'), Timestamp('2022-01-02 00:00:00')]
    """

    def convert(func: Callable, *args, **kwargs):
        if isinstance(time, Iterable):
            return [func(t, *args, **kwargs) for t in time]
        return func(time, *args, **kwargs)

    if time_format is TimeFormat.DATETIME:
        return convert(datetime.datetime.fromtimestamp)
    elif time_format is TimeFormat.PANDAS:
        return convert(pd.to_datetime, unit='s')
    return time


def format_number(data: Iterable, /, prec: PrecisionFormat, *, perc=False, plus=False):
    return [None if value is None else fmt.num(value, prec=int(prec), perc=perc, plus=plus) for value in data]


def opposite_side(side: int | str | OrderSide):
    """
    Returns the opposite side.

    Returned type = input parameter type.

    :examples:
    >>> opposite_side('BUY')
    'SELL'

    >>> opposite_side('SELL')
    'BUY'

    >>> opposite_side(OrderSide.SHORT) == OrderSide.LONG
    True

    >>> opposite_side(OrderSide.BUY) == OrderSide.SELL
    True
    """

    if isinstance(side, int):
        if side == BUY:
            return SELL
        elif side == SELL:
            return BUY
        raise ValueError(f"Side must be {BUY} or {SELL}, not {side}.")

    elif isinstance(side, str):
        if side.upper() == 'LONG':
            return 'SHORT'
        elif side.upper() == 'SHORT':
            return 'LONG'
        elif side.upper() == 'BUY':
            return 'SELL'
        elif side.upper() == 'SELL':
            return 'BUY'
        else:
            raise ValueError(f'Side must be BUY SELL LONG or SHORT, not {side}.')

    elif isinstance(side, OrderSide):
        return side.opposite()


def calculate_quantity(
        amount: float,
        price: float,
        leverage=1,
):
    """
    Calculates quantity.

    :param amount: Asset amount to spend on position.
    :param price: Unit share price
    :param leverage: Applied leverage (positive integer)

    :examples:
    >>> calculate_quantity(amount=1000, price=100, leverage=1)
    10.0

    >>> calculate_quantity(amount=100, price=1000, leverage=2)
    0.2
    """

    if leverage < 1:
        raise LeverageError('Leverage must be greater than or equal to 1.')

    quantity = amount / price * leverage
    return quantity


def liquidation_price(
        side: int | str | OrderSide,
        entry_price: float,
        quantity: float,
        leverage: int,
        balance: float,
):
    """
    Calculates liquidation price.

    Liquidation is an automatic procedure that occurs if the reserved margin
    is no longer sufficient to cover further losses from a position.

    # entry_price: 0.8
    # quantity: 1000
    # leverage: 10
    # side: BUY
    # balance: 100

    :examples:
    >>> liquidation_price(side=BUY, entry_price=0.8, quantity=1000, leverage=10, balance=100)
    0.70458
    """
    side = side_to_int(side)

    return entry_price * quantity * leverage / balance


def calculate_profit(side: int | str | OrderSide, entry_price: float, exit_price: float, quantity: float, leverage: int):
    """
    Calculates position profit.

    :examples:
    >>> calculate_profit(side=LONG, entry_price=100, exit_price=200, quantity=.5, leverage=1)
    50.0

    >>> calculate_profit(side=SHORT, entry_price=100, exit_price=200, quantity=.5, leverage=1)
    -50.0

    >>> calculate_profit(side=LONG, entry_price=100, exit_price=200, quantity=1, leverage=2)
    200
    """

    price_change = exit_price - entry_price if side_to_int(side) == LONG else entry_price - exit_price

    return price_change * quantity * leverage


def create_orders(
        symbol: str,
        money: float,
        side: int | OrderSide,
        current_price: float,
        order_price: float = None,
        order_profit_price: float = None,
        order_stop_price: float = None,
        order_trailing_stop_rate: float = None,
        order_trailing_stop_activation_price: float = None,
):
    from trader.core.model import Order

    if order_profit_price and order_stop_price:
        if (
                (side == BUY and order_profit_price <= order_stop_price)
                or (side == SELL and order_profit_price >= order_stop_price)
        ):
            raise ValueError('Invalid take profit and/or stop loss price.')

    quantity = calculate_quantity(amount=money, price=current_price)

    if order_price:
        entry_order = Order.limit(symbol=symbol, side=side, money=money, price=order_price, quantity=quantity)
    else:
        entry_order = Order.market(symbol=symbol, side=side, money=money, price=current_price, quantity=quantity)

    other_side = opposite_side(side)
    take_profit_order = stop_order = trailing_stop_order = None
    if order_profit_price:
        take_profit_order = Order.take_profit_market(symbol=symbol, side=other_side, stop_price=order_profit_price)
    if order_stop_price:
        stop_order = Order.stop_market(symbol=symbol, side=other_side, stop_price=order_stop_price)
    if order_trailing_stop_rate:
        trailing_stop_order = Order.trailing_stop_market_order(
            symbol=symbol,
            side=other_side,
            trailing_rate=order_trailing_stop_rate,
            activation_price=order_trailing_stop_activation_price,
        )

    return (
        entry_order,
        stop_order,
        take_profit_order,
        trailing_stop_order,
    )
