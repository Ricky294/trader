from __future__ import annotations

from trader.core.model import (
    MarketOrder, LimitOrder,
    StopMarketOrder, TakeProfitMarketOrder,
    TrailingStopMarketOrder,
)


class OrderGroup:

    __slots__ = (
        "entry_order",
        "exit_order",
        "stop_order",
        "profit_order",
        "trailing_order",
    )

    def __init__(
            self,
            entry_order: MarketOrder | LimitOrder,
            exit_order: MarketOrder | LimitOrder = None,
            stop_order: StopMarketOrder = None,
            profit_order: TakeProfitMarketOrder = None,
            trailing_order: TrailingStopMarketOrder = None,
    ):
        self.entry_order = entry_order
        self.exit_order = exit_order
        self.stop_order = stop_order
        self.profit_order = profit_order
        self.trailing_order = trailing_order
