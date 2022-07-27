from __future__ import annotations

from binance.client import Client

from trader.core.exception import PositionError
from trader.core.super_enum import OrderSide, OrderType, TimeInForce
from trader.core.model import Position
from trader.core.util.common import round_down


class BinancePosition(Position):

    def __init__(
            self,
            data: dict,
    ):
        quantity = float(data['positionAmt'])
        if quantity == .0:
            raise PositionError(f'No open {data["symbol"]!r} position.')

        super().__init__(
            symbol=data['symbol'],
            entry_time=data['updateTime'],
            entry_price=float(data['entryPrice']),
            amount=float(data['positionInitialMargin']),
            quantity=quantity,
            side=OrderSide.LONG if quantity > .0 else OrderSide.SHORT,
            leverage=int(data['leverage']),
        )
        self.__profit = float(data['unrealizedProfit'])

    def profit(self) -> float:
        return self.__profit


def stop_loss_market(
        client: Client,
        position: BinancePosition,
        stop_price: float,
        price_precision: int,
):
    stop_price = round_down(stop_price, price_precision)
    side = position.side.opposite().to_buy_sell()

    client.futures_create_order(
        symbol=position.symbol,
        type='STOP_MARKET',
        side=side,
        stopPrice=stop_price,
        closePosition='true',
    )


def take_profit_market(
        client: Client,
        position: BinancePosition,
        stop_price: float,
        price_precision: int,
):
    stop_price = round_down(stop_price, price_precision)

    side = position.side.opposite().to_buy_sell()

    client.futures_create_order(
        symbol=position.symbol,
        type='TAKE_PROFIT_MARKET',
        side=side,
        stopPrice=stop_price,
        closePosition='true',
    )


def close_position_limit(
        client: Client,
        position: BinancePosition,
        price: float,
        price_precision: int,
        time_in_force=TimeInForce.GTC,
):
    price = round_down(price, price_precision)
    side = position.side.opposite().to_buy_sell()
    time_in_force = str(time_in_force)

    client.futures_create_order(
        symbol=position.symbol,
        type=OrderType.LIMIT,
        side=side,
        quantity=abs(position.quantity),
        price=price,
        reduceOnly='true',
        timeInForce=str(time_in_force),
    )


def close_position_market(
        client: Client,
        position: BinancePosition,
):
    side = position.side.opposite().to_buy_sell()
    client.futures_create_order(
        symbol=position.symbol,
        type=OrderType.MARKET,
        side=side,
        quantity=abs(position.quantity),
        reduceOnly='true',
    )
