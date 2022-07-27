from __future__ import annotations

from trader.backtest.model.trailing_stop import BacktestTrailingStopMarketOrder
from trader.core.super_enum import OrderSide, OrderType
from trader.core.model import (
    Order,
    MarketOrder,
    LimitOrder,
    TakeProfitMarketOrder,
    StopMarketOrder,
    TrailingStopMarketOrder, Position, Balance,
)
from trader.data.model import Candles


def is_stop_loss_hit(
        high_price: float,
        low_price: float,
        order: StopMarketOrder,
):
    if order is None:
        return False

    return (
        low_price <= order.stop_price
        if order.side == OrderSide.SELL  # -> position.side == OrderSide.BUY
        else high_price >= order.stop_price
    )


def is_take_profit_hit(
        high_price: float,
        low_price: float,
        order: TakeProfitMarketOrder,
):
    if order is None:
        return False

    return (
        high_price >= order.stop_price
        if order.side == OrderSide.SELL   # -> position.side == OrderSide.BUY
        else low_price <= order.stop_price
    )


def is_limit_buy_hit(low_price: float, order: MarketOrder | LimitOrder):
    return (
            order.side == OrderSide.BUY
            and low_price < order.price
    )


def is_limit_sell_hit(high_price: float, order: MarketOrder | LimitOrder):
    return (
            order.side == OrderSide.SELL
            and high_price > order.price
    )


def is_trailing_stop_hit(
        high_price: float,
        low_price: float,
        order: BacktestTrailingStopMarketOrder,
):
    return order.side == OrderSide.SELL and high_price > 0


def is_order_filled(
        high_price: float,
        low_price: float,
        order: LimitOrder | StopMarketOrder | TakeProfitMarketOrder | BacktestTrailingStopMarketOrder | None
):
    if order is None:
        return False
    elif order.type == OrderType.MARKET:
        return True
    elif order.type == OrderType.LIMIT:
        return is_limit_buy_hit(
            low_price=low_price,
            order=order,
        ) or is_limit_sell_hit(
            high_price=high_price,
            order=order,
        )
    elif order.type == OrderType.TAKE_PROFIT_MARKET:
        return is_take_profit_hit(
            high_price=high_price,
            low_price=low_price,
            order=order,
        )
    elif order.type == OrderType.STOP_MARKET:
        return is_stop_loss_hit(
            high_price=high_price,
            low_price=low_price,
            order=order,
        )
    elif order.type == OrderType.TRAILING_STOP_MARKET:
        return is_trailing_stop_hit(
            high_price=high_price,
            low_price=low_price,
            order=order,
        )
    raise ValueError(f'Unsupported order: {order}')


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


def get_filled_orders(candles: Candles, orders: list[Order]) -> list[Order]:
    """
    Returns all filled orders in the order they got filled.

    :param candles:
    :param orders:
    :return:
    """
    def sort_orders():
        for order in orders:
            if order.type == OrderType.MARKET:
                yield -1, order
            else:
                if order.type == OrderType.LIMIT:
                    price = order.price
                elif order.type in [OrderType.STOP_MARKET, OrderType.TAKE_PROFIT_MARKET]:
                    price = order.stop_price
                else:   # order.type in [STOP_LIMIT, TAKE_PROFIT_LIMIT]
                    raise NotImplementedError

                if candles.latest_low_price < price < candles.latest_high_price:
                    yield abs(price - candles.latest_open_price), order

    orders = list(sort_orders())
    orders.sort(key=lambda o: o[0])
    return [order for _, order in orders]


def is_position_liquidated(
        side: OrderSide,
        leverage: int,
        average_entry_price: float,
        maintenance_margin_rate: float,
        candles: Candles,
):
    liq_price = calculate_liquidation_price(
        side=side,
        leverage=leverage,
        average_entry_price=average_entry_price,
        maintenance_margin_rate=maintenance_margin_rate
    )

    if side == 'LONG':
        return liq_price > candles.latest_low_price
    return liq_price < candles.high_prices


def calculate_liquidation_price(
        side: OrderSide,
        leverage: int,
        average_entry_price: float,
        maintenance_margin_rate: float
):
    """

    :param side
    :param average_entry_price:
    :param leverage:
    :param maintenance_margin_rate:
    :return:

    More info: https://help.bybit.com/hc/en-us/articles/360039261334-How-to-calculate-Liquidation-Price-Inverse-Contract-

    :example:
    >>> calculate_liquidation_price(OrderSide.LONG, 1000, 1, 0)
    500.0

    >>> calculate_liquidation_price(OrderSide.LONG, 8000, 50, 0.005)
    7881.773399014778

    >>> calculate_liquidation_price(OrderSide.SHORT, 8000, 50, 0.005)
    8121.827411167513
    """

    if side == OrderSide.LONG:
        return average_entry_price * leverage / (leverage + 1 - (maintenance_margin_rate * leverage))
    return average_entry_price * leverage / (leverage - 1 + (maintenance_margin_rate * leverage))


def get_position_liquidation_price(balance: Balance, position: Position | None):
    trade_ratio = position.amount / balance.available
    leveraged_ratio = trade_ratio * position.leverage

    # entry: 500
    # side: SHORT
    # trade ratio: 1
    # liquidation: 1000

    position.entry_price


def get_filled_first(
        high_price: float,
        low_price: float,
        open_price: float,
        take_profit_order: TakeProfitMarketOrder | None,
        stop_order: StopMarketOrder | None,
        exit_order: MarketOrder | LimitOrder | None,
        trailing_stop_order: TrailingStopMarketOrder | None,
):

    exit_hit = is_order_filled(high_price=high_price, low_price=low_price, order=exit_order)

    if exit_hit and exit_order.type == OrderType.MARKET:
        return exit_order

    take_profit_hit = is_order_filled(high_price=high_price, low_price=low_price, order=take_profit_order)
    stop_loss_hit = is_order_filled(high_price=high_price, low_price=low_price, order=stop_order)
    trailing_stop_hit = is_order_filled(high_price=high_price, low_price=low_price, order=trailing_stop_order)

    if take_profit_hit and stop_loss_hit:
        if get_closer_order(high_price, low_price, open_price, take_profit_order, stop_order).type == 'STOP_MARKET':
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
