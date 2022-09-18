from __future__ import annotations

from trader.core.const import Side
from trader.core.model import Position


def calculate_profit(side: Side, price: float, current_price: float, quantity: float, leverage: int):
    """
    Calculates position profit.

    :examples:
    >>> calculate_profit(side=Side.LONG, price=100, current_price=200, quantity=.5, leverage=1)
    50.0

    >>> calculate_profit(side=Side.SHORT, price=100, current_price=200, quantity=.5, leverage=1)
    -50.0

    >>> calculate_profit(side=Side.LONG, price=100, current_price=200, quantity=1, leverage=2)
    200
    """

    price_change = current_price - price if side is Side.LONG else price - current_price

    return price_change * quantity * leverage


def calculate_position_profit(position: Position, current_price: float):
    return calculate_profit(
        side=position.side,
        price=position.price,
        quantity=position.quantity,
        leverage=position.leverage,
        current_price=current_price,
    )


def is_position_liquidated(
        position: Position,
        low_price: float,
        high_price: float,
        available_balance: float,
):
    possible_liquidation_price = low_price if position.side is Side.LONG else high_price
    profit = calculate_position_profit(position, possible_liquidation_price)
    return available_balance + position.amount + profit <= 0
