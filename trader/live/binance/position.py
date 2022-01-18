from typing import Union

from binance.client import Client

from trader.core.model import Position, Order
from trader.core.enum import TimeInForce
from trader.core.util.trade import opposite_side

from .helpers import get_position_info


class BinancePosition(Position):

    def __init__(
        self,
        symbol: str,
        quantity: float,
        entry_price: float,
        leverage: int,
        client: Client,
        *args, **kwargs
    ):
        super().__init__(
            symbol=str(symbol),
            quantity=float(quantity),
            entry_price=float(entry_price),
            leverage=int(leverage)
        )
        self.client = client

    def profit(self) -> float:
        return float(get_position_info(self.client, self.symbol)["unrealizedProfit"])

    @classmethod
    def from_binance(cls, client: Client, data: dict):
        return cls(
            client=client,
            symbol=data["symbol"],
            quantity=data["positionAmt"],
            entry_price=data["entryPrice"],
            leverage=data["leverage"],
        )

    def reduce_position_market_order(self, quantity: float) -> Order:
        return Order.market(symbol=self.symbol, side=opposite_side(self.side), quantity=quantity)

    def close_position_market_order(self) -> Order:
        return Order.market(symbol=self.symbol, side=opposite_side(self.side), quantity=self.quantity)

    def close_position_limit_order(
        self,
        price: float,
        time_in_force: Union[str, TimeInForce] = "GTC",
    ) -> Order:
        order = Order.limit(
            symbol=self.symbol,
            side=opposite_side(self.side),
            quantity=self.quantity,
            price=price,
            time_in_force=time_in_force,
        )

        return order
