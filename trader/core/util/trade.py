from typing import Union

import numba
import numpy as np

from .common import generate_random_string, generate_ascii
from ..const.trade_actions import BUY, SELL

from ..enum import OrderSide


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


def opposite_side(side: int):
    if side == BUY:
        return SELL
    elif side == SELL:
        return BUY
    else:
        raise ValueError(f"Side must be {BUY} or {SELL}.")


@numba.jit(nopython=True)
def calculate_ha_open(open, close, ha_close):
    ha_open = np.empty(np.shape(open))
    ha_open[0] = (open[0] + close[0]) / 2

    for i in range(1, np.shape(open)[0]):
        ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2

    return ha_open


def generate_binance_client_order_id() -> str:
    max_char = 36

    zero_to_nine = "".join(generate_ascii(48, 58))
    a_to_z = "".join(generate_ascii(65, 91))
    A_to_Z = "".join(generate_ascii(97, 123))

    return generate_random_string(r".:/_-" + zero_to_nine + a_to_z + A_to_Z, max_char)


def to_heikin_ashi(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    ha_close = (open + high + low + close) / 4
    ha_open = calculate_ha_open(open, close, ha_close)
    ha_high = np.maximum.reduce((high, ha_open, ha_close))
    ha_low = np.minimum.reduce((low, ha_open, ha_close))

    return ha_open, ha_high, ha_low, ha_close


def get_side_by_quantity(quantity: Union[float, int]):
    return BUY if quantity > 0 else SELL


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
        side: Union[OrderSide, int],
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
        side: Union[OrderSide, str],
        leverage: int
):
    diff = entry_price * roe / leverage

    side = str(side).upper()

    if side == BUY:
        return entry_price + diff
    elif side == SELL:
        return entry_price - diff


def create_position(
        symbol: str,
        quantity: float,
        price: float = None,
        take_profit_price: float = None,
        stop_loss_price: float = None,
):
    from ..model import Order
    if take_profit_price is not None and stop_loss_price is not None:
        if (
                (quantity > 0 and take_profit_price <= stop_loss_price)
                or (quantity < 0 and take_profit_price >= stop_loss_price)
        ):
            raise ValueError("Invalid take profit and/or stop loss price.")

    side = BUY if quantity > 0 else SELL
    if price is None:
        entry_order = Order.market(symbol=symbol, side=side, quantity=quantity)
    else:
        entry_order = Order.limit(symbol=symbol, side=side, quantity=quantity, price=price)

    exit_side = opposite_side(side)
    take_profit_order = None
    stop_order = None
    if take_profit_price is not None:
        take_profit_order = Order.take_profit_market(symbol=symbol, side=exit_side, stop_price=take_profit_price)
    elif stop_loss_price is not None:
        stop_order = Order.stop_market(symbol=symbol, side=exit_side, stop_price=stop_loss_price)

    return entry_order, stop_order, take_profit_order
