from __future__ import annotations

from trader.core.const import OrderStatus
from trader.core.model import Order
from trader.data.model import Models


class Orders(Models[Order]):

    def _filter_status(self, symbol: str | None, *statuses: OrderStatus):
        if symbol:
            return [
                order
                for order in self
                if order.status in statuses
                and order.symbol == symbol
            ]

        return [
            order
            for order in self
            if order.status in statuses
        ]

    def open_orders(self, symbol: str = None):
        """
        Returns all NEW and PARTIALLY_FILLED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED)

    def new_orders(self, symbol: str = None):
        """
        Returns all NEW orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.NEW)

    def filled_orders(self, symbol: str = None):
        """
        Returns all FILLED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.FILLED)

    def partially_filled_orders(self, symbol: str = None):
        """
        Returns all PARTIALLY_FILLED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.PARTIALLY_FILLED)

    def canceled_orders(self, symbol: str = None):
        """
        Returns all CANCELED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.CANCELED)

    def pending_cancel_orders(self, symbol: str = None):
        """
        Returns all PENDING_CANCEL orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.PENDING_CANCEL)

    def expired_orders(self, symbol: str = None):
        """
        Returns all EXPIRED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.EXPIRED)

    def rejected_orders(self, symbol: str = None):
        """
        Returns all REJECTED orders.

        Filters on `symbol` if not None.
        """
        return self._filter_status(symbol, OrderStatus.REJECTED)

    @property
    def symbol(self):
        return [order.symbol for order in self]

    @property
    def side(self):
        return [order.side for order in self]

    @property
    def status(self):
        return [order.status for order in self]

    @property
    def type(self):
        return [order.type for order in self]

    @property
    def amount(self):
        return [order.amount for order in self]

    @property
    def quantity(self):
        return [order.quantity for order in self]

    @property
    def price(self):
        return [order.price for order in self]

    @property
    def stop_price(self):
        return [order.stop_price for order in self]

    @property
    def time_in_force(self):
        return [order.time_in_force for order in self]

    @property
    def close_position(self):
        return [order.close_position for order in self]

    @property
    def reduce_only(self):
        return [order.reduce_only for order in self]

    @property
    def activation_price(self):
        return [order.activation_price for order in self]

    @property
    def trailing_percentage(self):
        return [order.trailing_percentage for order in self]
