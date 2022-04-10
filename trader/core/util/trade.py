from __future__ import annotations

from trader.core.const.trade_actions import BUY, SELL
from trader.core.enum import OrderSide


def str_side_to_int(side: str):
    if side.upper() in ("BUY", "LONG"):
        return BUY
    elif side.upper() in ("SELL", "SHORT"):
        return SELL
    else:
        raise ValueError("Side must be BUY, SELL, LONG or SHORT.")


def int_side_to_str(side: int):
    if side == BUY:
        return "BUY"
    elif side == SELL:
        return "SELL"
    else:
        raise ValueError(f"Side must be {BUY} or {SELL}.")


def opposite_side(side: OrderSide | int):
    if int(side) == BUY:
        return SELL
    elif int(side) == SELL:
        return BUY
    else:
        raise ValueError(f"Side must be {BUY} or {SELL}.")


def get_side_by_quantity(quantity: float | int):
    return BUY if quantity > 0 else SELL


def calculate_money(price: float, quantity: float, leverage: int):
    return price * quantity * leverage


def reduce_quantity_with_fee(quantity: float, fee_rate: float):
    return quantity - calculate_quantity_fee(quantity=quantity, fee_rate=fee_rate)


def calculate_quantity_fee(quantity: float, fee_rate: float):
    return quantity * fee_rate


def reduce_money_with_fee(price: float, quantity: float, fee_rate: float, leverage: int):
    money = calculate_money(price=price, quantity=quantity, leverage=leverage)
    return money - (money * fee_rate * leverage)


def calculate_money_fee(money: float, fee_rate: float, leverage: int):
    return abs(money * fee_rate * leverage)


def calculate_quantity(
        side: int,
        balance: float,
        price: float,
        trade_ratio: float,
        leverage: int = 1,
):
    quantity = balance / price * trade_ratio * leverage
    return quantity if side == BUY else -quantity


def calculate_profit(entry_price: float, exit_price: float, quantity: float, leverage: int):
    return abs(entry_price - exit_price) * quantity * leverage


def calculate_pnl(
        entry_price: float,
        exit_price: float,
        quantity: float,
        side: OrderSide | int,
        leverage: int = 1,
):
    """
    :return: Tuple of 3: (initial margin, pnl, roe)
    """

    side = str(side).upper()

    if side == BUY:
        pnl = (exit_price - entry_price) * quantity
    elif side == SELL:
        pnl = (entry_price - exit_price) * quantity
    else:
        raise ValueError(f"Parameter side must be {BUY} or {SELL}")

    initial_margin = quantity * entry_price / leverage
    roe = pnl / initial_margin

    return initial_margin, pnl, roe


def calculate_target_price(
        entry_price: float,
        roe: float,
        side: OrderSide | str,
        leverage: int
):
    diff = entry_price * roe / leverage

    side = str(side).upper()

    if side == BUY:
        return entry_price + diff
    elif side == SELL:
        return entry_price - diff


def create_orders(
        symbol: str,
        money: float,
        side: int | OrderSide,
        entry_price: float = None,
        take_profit_price: float = None,
        stop_loss_price: float = None,
        trailing_stop_rate: float = None,
        trailing_stop_activation_price: float = None,
):
    from trader.core.model import Order

    if take_profit_price is not None and stop_loss_price is not None:
        if (
                (side == BUY and take_profit_price <= stop_loss_price)
                or (side == SELL and take_profit_price >= stop_loss_price)
        ):
            raise ValueError("Invalid take profit and/or stop loss price.")

    if entry_price is None:
        entry_order = Order.market(symbol=symbol, side=side, money=money)
    else:
        entry_order = Order.limit(symbol=symbol, side=side, money=money, price=entry_price)

    other_side = opposite_side(side)
    take_profit_order = stop_order = trailing_stop_order = None
    if take_profit_price is not None:
        take_profit_order = Order.take_profit_market(symbol=symbol, side=other_side, stop_price=take_profit_price)
    if stop_loss_price is not None:
        stop_order = Order.stop_market(symbol=symbol, side=other_side, stop_price=stop_loss_price)
    if trailing_stop_rate is not None:
        trailing_stop_order = Order.trailing_stop_market_order(
            symbol=symbol,
            side=other_side,
            trailing_rate=trailing_stop_rate,
            activation_price=trailing_stop_activation_price,
        )

    return entry_order, stop_order, take_profit_order, trailing_stop_order
