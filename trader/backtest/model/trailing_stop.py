from __future__ import annotations

from trader.core.super_enum import OrderSide
from trader.core.model import TrailingStopMarketOrder


class BacktestTrailingStopMarketOrder(TrailingStopMarketOrder):

    __slots__ = 'current_stop', 'stopped_at'

    def _update_stop_price(self, price: float):
        if self.stopped_at is None:
            if self.side == OrderSide.SELL:
                self.stop_price = price * (1 - self.trailing_rate)
            else:  # side == BUY
                self.stop_price = price * (1 + self.trailing_rate)

    def __init__(
            self,
            symbol: str,
            side: OrderSide,
            trailing_rate: float,
            current_price: float,
            activation_price: float = None,
            reduce_only=True,
    ):
        if activation_price is not None:
            if activation_price < current_price and side == OrderSide.SELL:
                raise ValueError('Order side must be BUY if activation price is below current price.')
            elif activation_price > current_price and side == OrderSide.BUY:
                raise ValueError('Order side must be SELL if activation price is above current price.')

        current_or_activation_price = activation_price if activation_price is not None else current_price
        super().__init__(
            symbol=symbol,
            side=side,
            trailing_rate=trailing_rate,
            activation_price=current_or_activation_price,
            reduce_only=reduce_only
        )
        self.current_stop = self._update_stop_price(current_price) if activation_price is None else None
        self.stopped_at = None

    def __call__(self, high_price: float, low_price: float):
        if self.stopped_at is None:
            if self.side == OrderSide.SELL:
                if self.current_stop is not None:
                    if low_price < self.current_stop:
                        self.stopped_at = self.current_stop

            else:
                self._update_stop_price()
