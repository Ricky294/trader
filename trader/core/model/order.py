from __future__ import annotations

from trader.core.enumerate import OrderSide, OrderType, TimeInForce, TimeFormat, SideFormat

from trader.core.util.common import round_down
from trader.core.util.trade import opposite_side, side_to_buy_sell, side_to_int, format_side
from trader.config import MONEY_PRECISION
from trader.data.typing import Side


class Order:

    __slots__ = (
        'order_id', 'status', 'symbol', 'type', 'side',
        'money', 'quantity', 'price', 'stop_price', 'close_position',
        'time_in_force', 'reduce_only', 'activation_price', 'trailing_rate',
    )

    def __str__(self):
        return 'Order (' + ', '.join([
            f'{attr}: {getattr(self, attr)}'
            for attr in self.__slots__
            if getattr(self, attr) is not None
        ]) + ')'

        return (
            f'Order (id: {self.order_id}'
            f', status: {self.status}'
            f', symbol: {self.symbol}'
            f', type: {self.type}'
            f', side: {side_to_buy_sell(self.side)}'
            f', money: {self.money:.{MONEY_PRECISION}f}',
            f', quantity: {self.quantity}',
            f', price: {self.price}',
            f', stop price: {self.stop_price}',
            f', close position: {self.close_position}',
            f', time in force: {self.time_in_force}',
            f', reduce only: {self.reduce_only}',
            f', activation price: {self.activation_price}',
            f', trailing rate: {self.trailing_rate})'
        )

    def to_list(self, time_format: TimeFormat, side_format: SideFormat):
        return [
            self.order_id, self.status, self.symbol, self.type, format_side(self.side, side_format),
            self.money, self.quantity, self.price, self.stop_price, self.close_position,
            self.time_in_force, self.reduce_only, self.activation_price, self.trailing_rate
        ]

    def to_dict(self, time_format: TimeFormat, side_format: SideFormat):
        return {
            'id': self.order_id,
            'status': self.status,
            'symbol': self.symbol,
            'type': self.type,
            'side': format_side(self.side, side_format),
            'money': self.money,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'close_position': self.close_position,
            'time_in_force': self.time_in_force,
            'reduce_only': self.reduce_only,
            'activation_price': self.activation_price,
            'trailing_rate': self.trailing_rate,
        }

    def __init__(
            self,
            symbol: str,
            type: str | OrderType,
            side: Side,
            quantity: float = None,
            money: float = None,
            order_id: int = None,
            status: str = None,
            price: float = None,
            stop_price: float = None,
            close_position=False,
            time_in_force: str = None,
            reduce_only=False,
            activation_price: float = None,
            trailing_rate: float = None,
    ):
        self.symbol = symbol
        self.side = side_to_int(side)
        self.type = str(type)
        self.money = money
        self.quantity = quantity
        self.price = price
        self.stop_price = stop_price
        self.trailing_rate = trailing_rate
        self.activation_price = activation_price
        self.close_position = close_position
        self.time_in_force = time_in_force
        self.reduce_only = reduce_only
        self.order_id = order_id
        self.status = status

    @property
    def is_taker(self) -> bool:
        """
        True if order is a market type order.

        - Taker orders are executed immediately and takes liquidity out of the order book (e.g. Market order)
        - Maker orders gets into the order book (e.g. Limit order)

        :return: bool
        """
        return 'MARKET' in self.type.upper()

    def opposite_side(self):
        return opposite_side(self.side)

    def to_binance_order(self, quantity: float, price_precision: int, quantity_precision: int):
        order = dict(symbol=self.symbol, type=str(self.type).upper(), side=side_to_buy_sell(self.side))
        if self.money is not None:
            order['quantity'] = round_down(quantity, quantity_precision)
        if self.price is not None:
            order['price'] = round_down(self.price, price_precision)
        if self.stop_price is not None:
            order['stopPrice'] = round_down(self.stop_price, price_precision)
        if self.time_in_force is not None:
            order['timeInForce'] = self.time_in_force.upper()
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
    def from_binance(data: dict) -> 'Order':
        order_type: str = data['type']

        if order_type == OrderType.LIMIT:
            return LimitOrder(
                order_id=data['orderId'],
                status=data['status'],
                symbol=data['symbol'],
                side=data['side'],
                price=float(data['price']),
                money=float(data['origQty']) * float(data['price']),
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
            side: OrderSide | str | int,
            money: float,
            quantity: float,
            price: float,
            reduce_only=False,
            order_id=None,
            status: str = None,
    ):
        return MarketOrder(
            symbol=symbol,
            side=side,
            money=money,
            quantity=quantity,
            price=price,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def limit(
            symbol: str,
            side: OrderSide | str | int,
            money: float,
            quantity: float,
            price: float,
            time_in_force: TimeInForce | str = 'GTC',
            reduce_only=False,
            order_id=None,
            status: str = None,
    ):
        return LimitOrder(
            symbol=symbol,
            side=side,
            money=money,
            quantity=quantity,
            price=price,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status
        )

    @staticmethod
    def stop_limit(
            symbol: str,
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
            money: float,
            quantity: float,
            price: float,
            order_id=None,
            status: str = None,
            reduce_only=False,
    ):
        super().__init__(
            symbol=symbol,
            side=side,
            type=OrderType.MARKET,
            quantity=quantity,
            price=price,
            money=money,
            reduce_only=reduce_only,
            order_id=order_id,
            status=status,
        )


class LimitOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide | str | int,
            money: float,
            quantity: float,
            price: float,
            order_id=None,
            status: str = None,
            time_in_force: str | TimeInForce = 'GTC',
            reduce_only=False,
    ):

        super().__init__(
            order_id=order_id,
            status=status,
            symbol=symbol,
            side=side,
            quantity=quantity,
            type=OrderType.LIMIT,
            time_in_force=time_in_force,
            money=money,
            price=price,
            reduce_only=reduce_only,
        )

    @property
    def quantity(self):
        return self.money / self.price


class TakeProfitMarketOrder(Order):

    def __init__(
            self,
            symbol: str,
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
            side: OrderSide | str | int,
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
