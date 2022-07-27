"""Implements core trading utility functions.

Functions:
    * side_to_int - Converts parameter `side` to its int representation.
    * side_to_buy_sell - Converts parameter `side` to str 'BUY' or 'SELL'.
    * opposite_side - Converts parameter `side` to its opposite (e.g. BUY -> SELL).
    * create_orders - Creates Order objects based on the parameters.
"""

from __future__ import annotations

from typing import Iterable, Literal

import trader.core.util.format as fmt
from trader.core.super_enum import OrderSide, OrderType
from trader.core.exception import LeverageError


def format_number(data: Iterable, /, prec: int, *, perc=False, plus=False):
    return [None if value is None else fmt.num(value, prec=prec, perc=perc, plus=plus) for value in data]


def calculate_quantity(
        amount: float,
        price: float,
        leverage: int,
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
        side: OrderSide,
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
    >>> liquidation_price(side=None, entry_price=0.8, quantity=1000, leverage=10, balance=100)
    0.70458
    """
    return entry_price * quantity * leverage / balance


def calculate_profit(side: OrderSide, entry_price: float, current_price: float, quantity: float, leverage: int):
    """
    Calculates position profit.

    :examples:
    >>> calculate_profit(side=OrderSide.LONG, entry_price=100, current_price=200, quantity=.5, leverage=1)
    50.0

    >>> calculate_profit(side=OrderSide.SHORT, entry_price=100, current_price=200, quantity=.5, leverage=1)
    -50.0

    >>> calculate_profit(side=OrderSide.LONG, entry_price=100, current_price=200, quantity=1, leverage=2)
    200
    """

    price_change = current_price - entry_price if side == OrderSide.LONG else entry_price - current_price

    return price_change * quantity * leverage


def calculate_fee(quantity: float, price: float, fee_rate: float, perc=False):
    """
    Fee calculation formula:
        amount * price * fee_rate

    :param quantity: Traded amount of asset.
    :param price: Asset price.
    :param fee_rate: Applied fee rate (percentage / 100).
    :param perc: Set it to True if fee_rate is in percentage.
    :return: fee

    >>> calculate_fee(quantity=1, price=10104, fee_rate=0.0004)
    4.0416

    >>> calculate_fee(quantity=1, price=10104, fee_rate=0.04, perc=True)
    4.0416
    """
    if perc:
        fee_rate = fee_rate / 100

    return quantity * price * fee_rate


def create_orders(
        symbol: str,
        amount: float,
        side: OrderSide,
        type: Literal[OrderType.LIMIT, OrderType.MARKET],
        price: float,
        leverage: int,
        profit_price: float = None,
        stop_price: float = None,
        trailing_stop_rate: float = None,
        trailing_stop_activation_price: float = None,
):
    from trader.core.model import Order

    if profit_price and stop_price:
        if (
                (side == OrderSide.BUY and profit_price <= stop_price)
                or (side == OrderSide.SELL and profit_price >= stop_price)
        ):
            raise ValueError('Invalid take profit and/or stop loss price.')

    quantity = calculate_quantity(amount=amount, price=price, leverage=leverage)
    entry_order = Order(symbol=symbol, side=side, type=type, amount=amount, price=price, quantity=quantity)

    other_side = side.opposite()
    take_profit_order = stop_order = trailing_stop_order = None
    if profit_price:
        take_profit_order = Order.take_profit_market(symbol=symbol, side=other_side, stop_price=profit_price)
    if stop_price:
        stop_order = Order.stop_market(symbol=symbol, side=other_side, stop_price=stop_price)
    if trailing_stop_rate:
        trailing_stop_order = Order.trailing_stop_market_order(
            symbol=symbol,
            side=other_side,
            trailing_rate=trailing_stop_rate,
            activation_price=trailing_stop_activation_price,
        )

    return (
        entry_order,
        stop_order,
        take_profit_order,
        trailing_stop_order,
    )
