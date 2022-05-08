"""Implements core trading utility functions.

Functions:
    * side_to_int - Converts parameter `side` to its int representation.
    * side_to_buy_sell - Converts parameter `side` to str 'BUY' or 'SELL'.
    * side_to_long_short - Converts parameter `side` to str 'LONG' or 'SHORT'.
    * opposite_side - Converts parameter `side` to its opposite (e.g. BUY --> SELL).
    * create_orders - Creates Order objects based on the parameters.
"""

from __future__ import annotations

from trader.core.const.trade_actions import BUY, SELL, LONG, SHORT
from trader.core.enumerate import OrderSide


def side_to_int(side: int | str | OrderSide):
    """
    Converts `side` to int

    :examples:
    >>> side_to_int(BUY) == BUY == LONG
    True

    >>> side_to_int("LONG") == BUY == LONG
    True

    >>> side_to_int("SHORT") == SELL == SHORT
    True

    >>> side_to_int(OrderSide.SELL) == SELL == SHORT
    True
    """

    if isinstance(side, int):
        if side in (BUY, SELL):
            return side
        raise ValueError(f"Param `side` (type: int) must be {BUY} or {SELL}")

    elif isinstance(side, str):
        if side.upper() in ("BUY", "LONG"):
            return BUY
        elif side.upper() in ("SELL", "SHORT"):
            return SELL
        raise ValueError("Param `side` (type: str) must be BUY, SELL, LONG or SHORT.")

    elif isinstance(side, OrderSide):
        return int(side)

    raise ValueError(f"Unsupported type for side: {type(side)}")


def side_to_buy_sell(side: int | str | OrderSide):
    """
    Converts parameter to 'BUY' or 'SELL' (str).

    :examples:
    >>> side_to_buy_sell("SHORT")
    'SELL'

    >>> side_to_buy_sell(BUY)
    'BUY'

    >>> side_to_buy_sell(OrderSide.LONG)
    'BUY'

    :return: str ('BUY' | 'SELL')
    :raises ValueError: If param side is invalid.
    """

    if isinstance(side, str):
        if side.upper() in ("SHORT", "SELL"):
            return "SELL"
        elif side.upper() in ("LONG", "BUY"):
            return "BUY"
        else:
            raise ValueError(f"Invalid side value: {side!r}")

    side = int(side)
    if side == BUY:
        return "BUY"
    elif side == SELL:
        return "SELL"
    raise ValueError(f"Side must be {BUY!r} or {SELL!r}.")


def side_to_long_short(side: int | str | OrderSide):
    """
    Converts parameter to 'LONG' or 'SHORT' (str).

    :examples:
    >>> side_to_long_short("SELL")
    'SHORT'

    >>> side_to_long_short(LONG)
    'LONG'

    >>> side_to_long_short(OrderSide.BUY)
    'LONG'

    :return: str ('LONG' | 'SHORT')
    :raises ValueError: If param side is invalid.
    """
    if isinstance(side, str):
        if side.upper() in ("SHORT", "SELL"):
            return "SHORT"
        elif side.upper() in ("LONG", "BUY"):
            return "LONG"
        else:
            raise ValueError(f"Invalid side value: {side!r}")

    side = int(side)
    if side == BUY:
        return "LONG"
    elif side == SELL:
        return "SHORT"
    raise ValueError(f"Side must be {LONG!r} or {SHORT!r}.")


def opposite_side(side: int | str | OrderSide):
    """
    Returns the opposite side.

    Returned type = input parameter type.

    :examples:
    >>> opposite_side("BUY")
    'SELL'

    >>> opposite_side("SELL")
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
        if side.upper() == "LONG":
            return "SHORT"
        elif side.upper() == "SHORT":
            return "LONG"
        elif side.upper() == "BUY":
            return "SELL"
        elif side.upper() == "SELL":
            return "BUY"
        else:
            raise ValueError(f"Side must be BUY SELL LONG or SHORT, not {side}.")

    elif isinstance(side, OrderSide):
        return side.opposite()


def position_quantity(
        amount: float,
        price: float,
        leverage: int,
):
    """
    Calculates position quantity.

    :param amount: Asset amount to spend on position.
    :param price: Unit share price
    :param leverage: Applied leverage (positive integer)

    :examples:
    >>> position_quantity(amount=1000, price=100, leverage=1)
    10.0

    >>> position_quantity(amount=100, price=1000, leverage=2)
    0.2
    """

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


def position_profit(side: int | str | OrderSide, entry_price: float, exit_price: float, quantity: float, leverage: int):
    """
    Calculates position profit.

    :examples:
    >>> position_profit(side=LONG, entry_price=100, exit_price=200, quantity=.5, leverage=1)
    50.0

    >>> position_profit(side=SHORT, entry_price=100, exit_price=200, quantity=.5, leverage=1)
    -50.0

    >>> position_profit(side=LONG, entry_price=100, exit_price=200, quantity=1, leverage=2)
    200
    """

    price_change = exit_price - entry_price if side_to_int(side) == LONG else entry_price - exit_price

    return price_change * quantity * leverage


def create_orders(
        symbol: str,
        money: float,
        side: int | OrderSide,
        price: float = None,
        profit_price: float = None,
        stop_price: float = None,
        trailing_stop_rate: float = None,
        trailing_stop_activation_price: float = None,
):
    from trader.core.model import Order

    if profit_price and stop_price:
        if (
                (side == BUY and profit_price <= stop_price)
                or (side == SELL and profit_price >= stop_price)
        ):
            raise ValueError("Invalid take profit and/or stop loss price.")

    if price:
        entry_order = Order.limit(symbol=symbol, side=side, money=money, price=price)
    else:
        entry_order = Order.market(symbol=symbol, side=side, money=money)

    other_side = opposite_side(side)
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
