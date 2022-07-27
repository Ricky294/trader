from __future__ import annotations

from trader.core.super_enum import OrderSide, TimeInForce, OrderType
from trader.core.util.common import round_down

from trader.data.model import Model


class Order(Model):

    def __init__(
            self,
            symbol: str,
            type: OrderType,
            side: OrderSide,
            order_id=None,
            time: float = None,
            quantity: float = None,
            amount: float = None,
            status: str = None,
            price: float = None,
            stop_price: float = None,
            close_position=False,
            time_in_force: TimeInForce = None,
            reduce_only=False,
            activation_price: float = None,
            trailing_rate: float = None,
    ):
        super(Order, self).__init__(time)
        self.order_id = order_id
        self.symbol = symbol
        self.side = side
        self.type = type
        self.amount = amount
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.trailing_rate = trailing_rate
        self.activation_price = activation_price
        self.close_position = close_position
        self.time_in_force = time_in_force
        self.reduce_only = reduce_only
        self.status = status

    @property
    def is_taker(self) -> bool:
        """
        True if order is a market type order.

        - Taker orders are executed immediately and takes liquidity out of the order book (e.g. Market order)
        - Maker orders gets into the order book (e.g. Limit order)

        :return: bool
        """
        return self.type.is_taker()

    @property
    def is_maker(self) -> bool:
        return self.type.is_maker()

    @property
    def opposite_side(self):
        return self.side.opposite()

    def to_binance_order(self, quantity: float, price_precision: int, quantity_precision: int):
        order = dict(symbol=self.symbol, type=str(self.type).upper(), side=self.side.to_buy_sell())
        if self.amount is not None:
            order['quantity'] = round_down(quantity, quantity_precision)
        if self.price is not None:
            order['price'] = round_down(self.price, price_precision)
        if self.stop_price is not None:
            order['stopPrice'] = round_down(self.stop_price, price_precision)
        if self.time_in_force is not None:
            order['timeInForce'] = str(self.time_in_force)
        if self.close_position:
            order['closePosition'] = str(self.close_position).lower()
        if self.reduce_only:
            order['reduceOnly'] = str(self.reduce_only).lower()
        if self.activation_price is not None:
            order['activationPrice'] = float(self.activation_price)
        if self.trailing_rate is not None:
            order['callbackRate'] = float(self.trailing_rate)
        return order

    @staticmethod
    def from_binance(data: dict) -> Order:
        order_type: str = data['type']

        if order_type == OrderType.LIMIT:
            return LimitOrder(
                order_id=data['orderId'],
                status=data['status'],
                symbol=data['symbol'],
                side=data['side'],
                price=float(data['price']),
                amount=float(data['origQty']) * float(data['price']),
                quantity=float(data['origQty']),
                time_in_force=data['timeInForce'],
            )
        elif order_type == OrderType.STOP_MARKET:
            return StopMarketOrder(
                symbol=data['symbol'],
                side=data['side'],
                stop_price=float(data['stopPrice']),
            )
        elif order_type == OrderType.TAKE_PROFIT_MARKET:
            return TakeProfitMarketOrder(
                symbol=data['symbol'],
                side=data['side'],
                stop_price=float(data['stopPrice']),
            )
        elif order_type == OrderType.TAKE_PROFIT_MARKET:
            return TrailingStopMarketOrder(
                symbol=data['symbol'],
                side=data['side'],
                activation_price=float(data['activationPrice']),
                trailing_rate=float(data['callbackRate']),
            )
        else:
            raise ValueError(f'Unsupported order type: {order_type}')

    @staticmethod
    def market(
            symbol: str,
            side: OrderSide,
            amount: float,
            quantity: float,
            price: float,
            reduce_only=False,
            order_id=None,
            status: str = None,
    ):
        return MarketOrder(
            symbol=symbol,
            side=side,
            amount=amount,
            quantity=quantity,
            price=price,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def limit(
            symbol: str,
            side: OrderSide,
            amount: float,
            price: float,
            quantity: float,
            time_in_force=TimeInForce.GTC,
            reduce_only=False,
            order_id=None,
            status: str = None,
    ):
        return LimitOrder(
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            quantity=quantity,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def stop_limit(
            symbol: str,
            side: OrderSide,
            price: float,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        return StopLimitOrder(
            symbol=symbol,
            side=side,
            price=price,
            stop_price=stop_price,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def take_profit_limit(
            symbol: str,
            side: OrderSide,
            price: float,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        return TakeProfitLimitOrder(
            symbol=symbol,
            side=side,
            price=price,
            stop_price=stop_price,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def stop_market(
            symbol: str,
            side: OrderSide,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        return StopMarketOrder(
            symbol=symbol,
            side=side,
            stop_price=stop_price,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def take_profit_market(
            symbol: str,
            side: OrderSide,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        return TakeProfitMarketOrder(
            symbol=symbol,
            side=side,
            stop_price=stop_price,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def trailing_stop_market_order(
            symbol: str,
            side: OrderSide,
            trailing_rate: float,
            activation_price: float = None,
            order_id=None,
            status: str = None,
            reduce_only=True,
    ):
        return TrailingStopMarketOrder(
            symbol=symbol,
            side=side,
            trailing_rate=trailing_rate,
            activation_price=activation_price,
            order_id=order_id,
            status=status,
            reduce_only=reduce_only,
        )


class TrailingStopMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            trailing_rate: float,
            activation_price: float = None,
            order_id=None,
            status: str = None,
            reduce_only=True,
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.TRAILING_STOP_MARKET,
            side=side,
            trailing_rate=trailing_rate,
            activation_price=activation_price,
            order_id=order_id,
            status=status,
            reduce_only=reduce_only,
        )


class MarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            amount: float,
            price: float,
            quantity: float,
            order_id=None,
            status: str = None,
            reduce_only=False,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.MARKET,
            amount=amount,
            price=price,
            quantity=quantity,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status,
        )


class LimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            amount: float,
            price: float,
            quantity: float,
            order_id=None,
            status: str = None,
            time_in_force=TimeInForce.GTC,
            reduce_only=False,
    ):

        super().__init__(
            order_id=order_id,
            status=status,
            symbol=symbol,
            side=side,
            type=OrderType.LIMIT,
            time_in_force=time_in_force,
            amount=amount,
            price=price,
            quantity=quantity,
            reduce_only=reduce_only,
        )

    @property
    def quantity(self):
        return self.amount / self.price


class TakeProfitMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.TAKE_PROFIT_MARKET,
            side=side,
            close_position=True,
            order_id=order_id,
            status=status
        )
        self.stop_price = stop_price


class TakeProfitLimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            price: float,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.TAKE_PROFIT_LIMIT,
            stop_price=stop_price,
            price=price,
            order_id=order_id,
            status=status
        )


class StopMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.STOP_MARKET,
            side=side,
            stop_price=stop_price,
            close_position=True,
            order_id=order_id,
            status=status
        )


class StopLimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            price: float,
            stop_price: float,
            order_id=None,
            status: str = None,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.STOP_LIMIT,
            price=price,
            stop_price=stop_price,
            order_id=order_id,
            status=status
        )
