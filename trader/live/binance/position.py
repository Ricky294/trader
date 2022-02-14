from typing import Union

from binance import Client

from trader.core.exception import PositionError
from trader.core.const.trade_actions import LONG, SHORT
from trader.core.enum import TimeInForce
from trader.core.model import Position
from trader.core.util.common import round_down
from trader.core.util.trade import opposite_side, int_side_to_str


class BinancePosition(Position):

    def __init__(
            self,
            data: dict,
    ):
        quantity = float(data["positionAmt"])
        if quantity == .0:
            raise PositionError(f"No open {data['symbol']!r} position.")

        super(BinancePosition, self).__init__(
            entry_time=data["updateTime"],
            symbol=data["symbol"],
            leverage=int(data["leverage"]),
            entry_price=float(data["entryPrice"]),
            money=float(data["positionInitialMargin"]),
            side=LONG if quantity > .0 else SHORT,
        )
        self.quantity = quantity
        self.__profit = float(data["unrealizedProfit"])

    def profit(self) -> float:
        return self.__profit


def stop_loss_market(
        client: Client,
        position: BinancePosition,
        stop_price: float,
        price_precision: int,
):
    stop_price = round_down(stop_price, price_precision)
    side = int_side_to_str(opposite_side(position.side))

    client.futures_create_order(
        symbol=position.symbol,
        type="STOP_MARKET",
        side=side,
        stopPrice=stop_price,
        closePosition="true",
    )


def take_profit_market(
        client: Client,
        position: BinancePosition,
        stop_price: float,
        price_precision: int,
):
    stop_price = round_down(stop_price, price_precision)
    side = int_side_to_str(opposite_side(position.side))

    client.futures_create_order(
        symbol=position.symbol,
        type="TAKE_PROFIT_MARKET",
        side=side,
        stopPrice=stop_price,
        closePosition="true",
    )


def close_position_limit(
        client: Client,
        position: BinancePosition,
        price: float,
        price_precision: int,
        time_in_force: Union[TimeInForce, str] = "GTC",
):
    price = round_down(price, price_precision)
    side = int_side_to_str(opposite_side(position.side))
    time_in_force = str(time_in_force)

    client.futures_create_order(
        symbol=position.symbol,
        type="LIMIT",
        side=side,
        quantity=abs(position.quantity),
        price=price,
        reduceOnly="true",
        timeInForce=str(time_in_force),
    )


def close_position_market(
        client: Client,
        position: BinancePosition,
):
    side = int_side_to_str(opposite_side(position.side))
    client.futures_create_order(
        symbol=position.symbol,
        type="MARKET",
        side=side,
        quantity=abs(position.quantity),
        reduceOnly="true",
    )
