from typing import Optional, Union

from trader.core.model import MarketOrder, LimitOrder, TakeProfitMarketOrder, StopMarketOrder, Order
from trader.core.const.trade_actions import BUY, SELL


def is_stop_loss_hit(
        high_price: float,
        low_price: float,
        order: Optional[StopMarketOrder],
):
    if order is None:
        return False

    return (
        low_price <= order.stop_price
        if order.side == SELL  # -> position.side == BUY
        else high_price >= order.stop_price
    )


def is_take_profit_hit(
        high_price: float,
        low_price: float,
        order: Optional[TakeProfitMarketOrder],
):
    if order is None:
        return False

    return (
        high_price >= order.stop_price
        if order.side == SELL   # -> position.side == BUY
        else low_price <= order.stop_price
    )


def is_limit_buy_hit(low_price: float, order: Optional[Union[MarketOrder, LimitOrder]]):
    return (
            order.side == BUY
            and low_price < order.price
    )


def is_limit_sell_hit(high_price: float, order: Optional[Union[MarketOrder, LimitOrder]]):
    return (
            order.side == SELL
            and high_price > order.price
    )


def is_order_filled(
        high_price: float,
        low_price: float,
        order: Optional[Union[MarketOrder, LimitOrder, StopMarketOrder, TakeProfitMarketOrder]]
):

    if order is None:
        return False
    elif order.type == "MARKET":
        return True
    elif order.type == "LIMIT":
        return is_limit_buy_hit(
            low_price=low_price,
            order=order,
        ) or is_limit_sell_hit(
            high_price=high_price,
            order=order,
        )
    elif order.type == "TAKE_PROFIT_MARKET":
        return is_take_profit_hit(
            high_price=high_price,
            low_price=low_price,
            order=order,
        )
    elif order.type == "STOP_MARKET":
        return is_stop_loss_hit(
            high_price=high_price,
            low_price=low_price,
            order=order,
        )
    raise ValueError(f"Unsupported order: {order}")


def get_closer_order(
        high_price: float,
        low_price: float,
        open_price: float,
        order1: Order,
        order2: Order,
):

    high_distance = high_price - open_price
    low_distance = open_price - low_price

    ord1_distance = abs(open_price - (order1.price if order1.price is not None else order1.stop_price))
    ord2_distance = abs(open_price - (order2.price if order2.price is not None else order2.stop_price))

    if high_distance / ord1_distance > low_distance / ord2_distance:
        return order1

    return order2


def get_filled_first(
        high_price: float,
        low_price: float,
        open_price: float,
        take_profit_order: Optional[TakeProfitMarketOrder],
        stop_order: Optional[StopMarketOrder],
        exit_order: Optional[Union[MarketOrder, LimitOrder]],
):

    exit_hit = is_order_filled(high_price=high_price, low_price=low_price, order=exit_order)

    if exit_hit and exit_order.type == "MARKET":
        return exit_order

    take_profit_hit = is_order_filled(high_price=high_price, low_price=low_price, order=take_profit_order)
    stop_loss_hit = is_order_filled(high_price=high_price, low_price=low_price, order=stop_order)

    if take_profit_hit and stop_loss_hit:
        if get_closer_order(high_price, low_price, open_price, take_profit_order, stop_order).type == "STOP_MARKET":
            take_profit_hit = False
        else:
            stop_loss_hit = False

    if exit_hit:
        params = dict(high_price=high_price, low_price=low_price, open_price=open_price, order1=exit_order)
        if take_profit_hit:
            return get_closer_order(**params, order2=take_profit_order)
        elif stop_loss_hit:
            return get_closer_order(**params, order2=stop_order)
    else:   # exit not hit
        if take_profit_hit:
            return take_profit_order
        elif stop_loss_hit:
            return stop_order
