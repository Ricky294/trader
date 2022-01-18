from typing import Union

from ..const.trade_actions import BUY as TA_BUY
from ..const.trade_actions import SELL as TA_SELL

from ..util.common import round_down
from ..util.trade import opposite_side

from ..enum.order import OrderSide, OrderType, TimeInForce


class Order:

    __slots__ = (
        "order_id",
        "status",
        "symbol",
        "type",
        "side",
        "quantity",
        "price",
        "stop_price",
        "close_position",
        "time_in_force",
        "reduce_only",
    )

    def __init__(
            self,
            symbol: str,
            type: Union[OrderType, str],
            side: Union[OrderSide, str, int],
            order_id: int = None,
            status: str = None,
            quantity: float = None,
            price: float = None,
            stop_price: float = None,
            close_position=False,
            time_in_force: str = None,
            reduce_only=False,
    ):
        self.side = int(side)
        if self.side not in (TA_BUY, TA_SELL):
            raise ValueError(f"Side must be {TA_BUY} or {TA_SELL}. Invalid value: {self.side}.")

        self.symbol = symbol
        self.type = str(type)
        if quantity is not None:
            self.quantity = abs(float(quantity))
        else:
            self.quantity = None
        self.price = price
        self.stop_price = stop_price
        self.close_position = close_position
        self.time_in_force = time_in_force
        self.reduce_only = reduce_only
        self.order_id = order_id
        self.status = status

    def side_as_str(self):
        return "BUY" if self.side == TA_BUY else "SELL"

    def opposite_side(self):
        return opposite_side(self.side)

    def to_binance_order(self, price_precision: int, quantity_precision: int):
        order = dict(symbol=self.symbol, type=str(self.type).upper(), side=str(self.side).upper())
        if self.quantity is not None:
            order["quantity"] = str(round_down(abs(self.quantity), quantity_precision))
        if self.price is not None:
            order["price"] = round_down(self.price, price_precision)
        if self.stop_price is not None:
            order["stopPrice"] = round_down(self.stop_price, price_precision)
        if self.close_position is not None:
            order["closePosition"] = str(self.close_position).lower()
        if self.time_in_force is not None:
            order["timeInForce"] = self.time_in_force
        if self.reduce_only is not None:
            order["reduceOnly"] = str(self.reduce_only).lower()
        return order

    @staticmethod
    def from_binance(data: dict) -> 'Order':
        order_type: str = data["type"]
        if order_type == OrderType.MARKET.value:
            return MarketOrder(
                symbol=data["symbol"],
                side=data["side"],
                quantity=float(data["origQty"]),
            )
        elif order_type == OrderType.LIMIT.value:
            return LimitOrder(
                symbol=data["symbol"],
                side=data["side"],
                price=float(data["price"]),
                quantity=float(data["origQty"]),
                time_in_force=data["timeInForce"],
            )
        elif order_type == OrderType.STOP_MARKET.value:
            return StopMarketOrder(
                symbol=data["symbol"],
                side=data["side"],
                stop_price=float(data["stopPrice"]),
            )
        elif order_type == OrderType.TAKE_PROFIT_MARKET.value:
            return TakeProfitMarketOrder(
                symbol=data["symbol"],
                side=data["side"],
                stop_price=float(data["stopPrice"]),
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

    @staticmethod
    def market(
        symbol: str,
        side: Union[OrderSide, str, int],
        quantity: float,
    ):
        return MarketOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
        )

    @staticmethod
    def limit(
        symbol: str,
        side: Union[OrderSide, str, int],
        quantity: float,
        price: float,
        time_in_force: Union[TimeInForce, str] = "GTC",
    ):
        return LimitOrder(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
        )

    @staticmethod
    def stop_limit(
        symbol: str,
        side: Union[OrderSide, str, int],
        price: float,
        stop_price: float,
    ):
        return StopLimitOrder(
            symbol=symbol,
            side=side,
            price=price,
            stop_price=stop_price,
        )

    @staticmethod
    def take_profit_limit(
        symbol: str,
        side: Union[OrderSide, str, int],
        price: float,
        stop_price: float,
    ):
        return TakeProfitLimitOrder(
            symbol=symbol,
            side=side,
            price=price,
            stop_price=stop_price,
        )

    @staticmethod
    def stop_market(
        symbol: str,
        side: Union[OrderSide, str, int],
        stop_price: float,
    ):
        return StopMarketOrder(
            symbol=symbol,
            side=side,
            stop_price=stop_price,
        )

    @staticmethod
    def take_profit_market(
        symbol: str,
        side: Union[OrderSide, str, int],
        stop_price: float,
    ):
        return TakeProfitMarketOrder(
            symbol=symbol,
            side=side,
            stop_price=stop_price,
        )

    def __str__(self):
        return str(self.__dict__)


class MarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            quantity: float,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.MARKET,
            quantity=quantity,
        )


class LimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            quantity: float,
            price: float,
            time_in_force: Union[str, TimeInForce] = "GTC",
    ):

        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.LIMIT,
            time_in_force=time_in_force,
            quantity=quantity,
            price=price,
        )


class TakeProfitMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            stop_price: float,
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.TAKE_PROFIT_MARKET,
            side=side,
            close_position=True,
        )
        self.stop_price = stop_price


class TakeProfitLimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            price: float,
            stop_price: float,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.TAKE_PROFIT_LIMIT,
            stop_price=stop_price,
            price=price,
        )


class StopMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            stop_price: float,
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.STOP_MARKET,
            side=side,
            stop_price=stop_price,
        )


class StopLimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: Union[OrderSide, str, int],
            price: float,
            stop_price: float,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.STOP_LIMIT,
            price=price,
            stop_price=stop_price,
        )
