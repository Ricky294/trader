from __future__ import annotations

from typing import Iterable

from trader.core.model import Order
from trader.data.model import Columnar


class Orders(Columnar):

    def __init__(self, orders: Iterable[Order]):
        super().__init__()
        self.id = [order.order_id for order in orders]
        self.status = [order.status for order in orders]
        self.symbol = [order.symbol for order in orders]
        self.type = [order.type for order in orders]
        self.side = [order.side for order in orders]
        self.amount = [order.amount for order in orders]
        self.quantity = [order.quantity for order in orders]
        self.price = [order.price for order in orders]
        self.stop_price = [order.stop_price for order in orders]
        self.close_position = [order.close_position for order in orders]
        self.time_in_force = [order.time_in_force for order in orders]
        self.reduce_only = [order.reduce_only for order in orders]
        self.activation_price = [order.activation_price for order in orders]
        self.trailing_rate = [order.trailing_rate for order in orders]
