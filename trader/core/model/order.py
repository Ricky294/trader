from __future__ import annotations

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Iterable
from itertools import count

from trader.core.const import Side, TimeInForce, OrderType, OrderStatus, Market
from trader.core.model import Position
from trader.data.model import Model, Symbol

from util.format_util import round_down, normalize_data_types


instance_counter = count(1)


@dataclass(frozen=True, kw_only=True)
class Order(Model, abc.ABC):
    __count: int = field(default_factory=lambda: next(instance_counter), init=False, repr=False)

    symbol: Symbol
    side: Side
    type: OrderType
    reduce_only: bool
    close_position: bool
    price: float = None
    stop_price: float = None
    quantity: float = None
    amount: float = None
    time_in_force: TimeInForce = None
    activation_price: float = None
    trailing_percentage: float = None
    status: OrderStatus = OrderStatus.NEW

    def _get_binance_futures_symbol_info(self):
        from trader.live.binance.helpers import get_futures_symbol_info
        return get_futures_symbol_info(symbol=self.symbol.pair)

    def is_stop_limit(self):
        """True if order type is either stop loss limit or take profit limit."""
        return self.type in {OrderType.STOP_LIMIT, OrderType.TAKE_PROFIT_LIMIT}

    @abc.abstractmethod
    def to_binance(self) -> dict[str, str | int | float | bool]:
        order = dict(
            symbol=self.symbol.pair.upper(),
            side=self.side.to_buy_sell(),
            type=self.type.to_binance(),
        )

        return order

    @staticmethod
    def from_binance(data: dict) -> Order:
        data = normalize_data_types(data)

        kwargs = dict(
            id=data['orderId'],
            symbol=data['symbol'],
            side=Side.from_value(data['side']),
            type=OrderType.from_binance(data['type']),
            status=OrderStatus.from_value(data['status']),
            create_time=datetime.fromtimestamp(data['updateTime'] / 1000),
            reduce_only=data['reduceOnly'],
            close_position=data['closePosition'],
        )

        if data['price'] != 0:
            kwargs['price'] = data['price']
        if kwargs['type'].is_maker():
            kwargs['time_in_force'] = TimeInForce.from_value(data['timeInForce'])
        if data['stopPrice'] != 0:
            kwargs['stop_price'] = data['stopPrice']
        if data['origQty'] != 0:
            kwargs['quantity'] = data['origQty']

            def get_price():
                if data['price'] == 0:
                    from trader.live.binance.helpers import get_current_price
                    return get_current_price(symbol=data['symbol'], market=Market.FUTURES)
                else:
                    return data['price']

            kwargs['amount'] = data['origQty'] * get_price()
        if 'activationPrice' in data:
            kwargs['activation_price'] = data['activationPrice']
        if 'callbackRate' in data:
            kwargs['trailing_percentage'] = data['callbackRate']

        order_class = kwargs.pop('type').to_order_class()
        try:
            return order_class(**kwargs)
        except TypeError as e:
            if 'close_position' in str(e):
                kwargs.pop('close_position')
            elif 'reduce_only' in str(e):
                kwargs.pop('reduce_only')

            return order_class(**kwargs)

    @classmethod
    def market(
            cls,
            symbol: Symbol,
            side: Side,
            quantity: float,
            amount: float,
            reduce_only: bool,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status: OrderStatus = OrderStatus.NEW,
    ):
        return MarketOrder(
            symbol=symbol,
            side=side,
            id=id,
            create_time=create_time,
            status=status,
            quantity=quantity,
            amount=amount,
            reduce_only=reduce_only,
        )

    @classmethod
    def limit(
            cls,
            symbol: Symbol,
            side: Side,
            amount: float,
            quantity: float,
            price: float,
            time_in_force: TimeInForce,
            reduce_only: bool,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status: OrderStatus = OrderStatus.NEW,
    ):
        return LimitOrder(
            symbol=symbol,
            side=side,
            status=status,
            id=id,
            create_time=create_time,
            quantity=quantity,
            amount=amount,
            price=price,
            time_in_force=time_in_force,
            reduce_only=reduce_only,
        )

    @classmethod
    def stop_limit(
            cls,
            symbol: Symbol,
            side: Side,
            price: float,
            quantity: float,
            amount: float,
            stop_price: float,
            time_in_force=TimeInForce.GTC,
            id: Any =None,
            create_time: float | datetime = datetime.now(),
            status=OrderStatus.NEW,
    ):
        return StopLimitOrder(
            create_time=create_time,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            amount=amount,
            time_in_force=time_in_force,
            stop_price=stop_price,
            id=id,
            status=status,
        )

    @classmethod
    def take_profit_limit(
            cls,
            symbol: Symbol,
            side: Side,
            price: float,
            quantity: float,
            amount: float,
            stop_price: float,
            time_in_force=TimeInForce.GTC,
            id: Any =None,
            create_time: float | datetime = datetime.now(),
            status=OrderStatus.NEW,
    ):
        return TakeProfitLimitOrder(
            create_time=create_time,
            symbol=symbol,
            side=side,
            price=price,
            quantity=quantity,
            amount=amount,
            time_in_force=time_in_force,
            stop_price=stop_price,
            id=id,
            status=status,
        )

    @classmethod
    def stop_market(
            cls,
            symbol: Symbol,
            side: Side,
            stop_price: float,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status=OrderStatus.NEW,
    ):
        return StopMarketOrder(
            create_time=create_time,
            symbol=symbol,
            side=side,
            stop_price=stop_price,
            id=id,
            status=status,
        )

    @classmethod
    def take_profit_market(
            cls,
            symbol: Symbol,
            side: Side,
            stop_price: float,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status=OrderStatus.NEW,
    ):
        return TakeProfitMarketOrder(
            create_time=create_time,
            symbol=symbol,
            side=side,
            stop_price=stop_price,
            id=id,
            status=status,
        )

    @classmethod
    def trailing_stop_market_order(
            cls,
            symbol: Symbol,
            side: Side,
            trailing_percentage: float,
            activation_price: float = None,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status=OrderStatus.NEW,
    ):
        return TrailingStopMarketOrder(
            symbol=symbol,
            side=side,
            create_time=create_time,
            trailing_percentage=trailing_percentage,
            activation_price=activation_price,
            id=id,
            status=status,
        )

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


class MarketOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            quantity: float,
            amount: float,
            reduce_only: bool,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.MARKET,
            side=side,
            status=status,
            id=id,
            create_time=create_time,
            reduce_only=reduce_only,
            amount=amount,
            quantity=quantity,
            close_position=False,
        )

    @classmethod
    def close_position(
            cls,
            position: Position,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status: OrderStatus = OrderStatus.NEW,
    ):
        return cls(
            id=id,
            create_time=create_time,
            status=status,
            symbol=position.symbol,
            side=position.side.opposite(),
            amount=position.amount,
            quantity=position.quantity,
            reduce_only=True,
        )

    def to_binance(self) -> dict[str, Any]:
        order = super().to_binance()

        # closePosition=True cannot be sent, Error code: -4136

        info = self._get_binance_futures_symbol_info()
        order['quantity'] = round_down(self.quantity, info.quantity_precision)
        order['reduceOnly'] = self.reduce_only

        return order


class StopMarketOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            stop_price: float,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            id=id,
            create_time=create_time,
            symbol=symbol,
            type=OrderType.STOP_MARKET,
            side=side,
            stop_price=stop_price,
            status=status,
            reduce_only=True,
            close_position=True,
        )

    def to_binance(self):
        order = super().to_binance()

        info = self._get_binance_futures_symbol_info()
        order['stopPrice'] = round_down(self.stop_price, info.price_precision)
        order['closePosition'] = self.close_position

        return order


class TakeProfitMarketOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            stop_price: float,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            id=id,
            create_time=create_time,
            symbol=symbol,
            type=OrderType.TAKE_PROFIT_MARKET,
            side=side,
            stop_price=stop_price,
            status=status,
            reduce_only=True,
            close_position=True,
        )

    def to_binance(self):
        order = super().to_binance()

        info = self._get_binance_futures_symbol_info()
        order['stopPrice'] = round_down(self.stop_price, info.price_precision)
        order['closePosition'] = self.close_position

        return order


class LimitOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            quantity: float,
            amount: float,
            price: float,
            reduce_only: bool,
            time_in_force: TimeInForce = TimeInForce.GTC,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            symbol=symbol,
            type=OrderType.LIMIT,
            side=side,
            status=status,
            price=price,
            quantity=quantity,
            amount=amount,
            time_in_force=time_in_force,
            id=id,
            create_time=create_time,
            reduce_only=reduce_only,
            close_position=False,
        )

    @classmethod
    def close_position(
            cls,
            position: Position,
            price: float,
            time_in_force=TimeInForce.GTC,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
            status: OrderStatus = OrderStatus.NEW,
    ):
        return cls(
            id=id,
            create_time=create_time,
            status=status,
            symbol=position.symbol,
            side=position.side.opposite(),
            amount=position.amount,
            quantity=position.quantity,
            price=price,
            time_in_force=time_in_force,
            reduce_only=True,
        )

    def to_binance(self):
        order = super().to_binance()

        # Error code=-4136: closePosition=True cannot be sent
        # Error code=-2022: ReduceOnly Order is rejected. -> In case of no open position on the opposite side.

        info = self._get_binance_futures_symbol_info()
        order['quantity'] = round_down(self.quantity, info.quantity_precision)
        order['price'] = round_down(self.price, info.price_precision)
        order['timeInForce'] = str(self.time_in_force)
        order['reduceOnly'] = self.reduce_only

        return order


class StopLimitOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            price: float,
            stop_price: float,
            quantity: float,
            amount: float,
            time_in_force: TimeInForce = TimeInForce.GTC,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            id=id,
            create_time=create_time,
            symbol=symbol,
            type=OrderType.STOP_LIMIT,
            side=side,
            status=status,
            price=price,
            time_in_force=time_in_force,
            quantity=quantity,
            amount=amount,
            stop_price=stop_price,
            reduce_only=True,
            close_position=True,
        )

    def to_limit_order(self, id: Any | None = None, create_time: float | datetime = datetime.now()):
        return LimitOrder(
            id=id,
            create_time=create_time,
            symbol=self.symbol,
            side=self.side,
            amount=self.amount,
            quantity=self.quantity,
            price=self.price,
            time_in_force=self.time_in_force,
            reduce_only=True,
        )

    def to_binance(self):
        order = super().to_binance()

        # APIError(code=-1106): Parameter 'reduceOnly' sent when not required. -> Do not send reduceOnly

        info = self._get_binance_futures_symbol_info()
        order['quantity'] = round_down(self.quantity, info.quantity_precision)
        order['price'] = round_down(self.price, info.price_precision)
        order['timeInForce'] = str(self.time_in_force)
        order['stopPrice'] = round_down(self.stop_price, info.price_precision)
        order['closePosition'] = self.close_position

        return order


class TakeProfitLimitOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            price: float,
            stop_price: float,
            quantity: float,
            amount: float,
            time_in_force: TimeInForce = TimeInForce.GTC,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),
    ):
        super().__init__(
            id=id,
            create_time=create_time,
            symbol=symbol,
            type=OrderType.TAKE_PROFIT_LIMIT,
            side=side,
            status=status,
            stop_price=stop_price,
            price=price,
            time_in_force=time_in_force,
            quantity=quantity,
            amount=amount,
            reduce_only=True,
            close_position=True,
        )

    def to_limit_order(self, id: Any | None = None, create_time: float | datetime = datetime.now()):
        return LimitOrder(
            id=id,
            create_time=create_time,
            symbol=self.symbol,
            side=self.side,
            amount=self.amount,
            quantity=self.quantity,
            price=self.price,
            time_in_force=self.time_in_force,
            reduce_only=True,
        )

    def to_binance(self):
        order = super().to_binance()

        # APIError(code=-1106): Parameter 'reduceOnly' sent when not required. -> Do not send reduceOnly

        info = self._get_binance_futures_symbol_info()
        order['quantity'] = round_down(self.quantity, info.quantity_precision)
        order['price'] = round_down(self.price, info.price_precision)
        order['timeInForce'] = str(self.time_in_force)
        order['stopPrice'] = round_down(self.stop_price, info.price_precision)
        order['closePosition'] = self.close_position

        return order


class TrailingStopMarketOrder(Order):

    def __init__(
            self,
            symbol: Symbol,
            side: Side,
            trailing_percentage: float,
            activation_price: float = None,
            status: OrderStatus = OrderStatus.NEW,
            id: Any = None,
            create_time: float | datetime = datetime.now(),

    ):
        super().__init__(
            id=id,
            create_time=create_time,
            symbol=symbol,
            type=OrderType.TRAILING_STOP_MARKET,
            side=side,
            status=status,
            reduce_only=True,
            close_position=True,
            trailing_percentage=trailing_percentage,
            activation_price=activation_price
        )

    def to_binance(self) -> dict[str, str | int | float | bool]:
        order = super().to_binance()
        order['callbackRate'] = float(self.trailing_percentage)
        order['activationPrice'] = float(self.activation_price)
        return order


def get_active_orders(orders: Iterable[Order]) -> list[Order]:
    """
    Returns all order from orders where status is NEW or PARTIALLY_FILLED.
    """

    return [
        order for order in orders
        if order.status in {OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED}
    ]


def get_reduce_orders(orders: Iterable[Order]) -> list[Order]:
    """
    Returns all order from orders where reduce_only or close_position is True.
    """

    return [
        order for order in orders
        if is_reduce_order(order)
    ]


def is_reduce_order(order: Order):
    return order.reduce_only or order.close_position


def is_close_order(order: Order):
    return order.close_position


def get_add_orders(orders: Iterable[Order]) -> list[Order]:
    """
    Returns all order from orders where reduce_only and close_position is False.
    """

    return [
        order for order in orders
        if is_add_order(order)
    ]


def is_add_order(order: Order):
    return not order.reduce_only and not order.close_position
