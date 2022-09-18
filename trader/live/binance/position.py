from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from trader.core.const import Side
from trader.core.model import Position
from util.format_util import normalize_data_types, snake_case


@dataclass(frozen=True)
class BinancePosition(Position):

    initial_margin: float
    maint_margin: float
    open_order_initial_margin: float
    isolated: bool
    max_notional: float
    position_side: str
    notional: float
    isolated_wallet: float
    bid_notional: float
    ask_notional: float

    @classmethod
    def from_dict(
            cls,
            pos: dict[str, Any],
    ):
        pos = normalize_data_types(pos)
        pos = {snake_case(key): value for key, value in pos.items()}

        return cls(
            fee=.0,
            state=0,
            create_time=datetime.fromtimestamp(pos.pop('update_time') / 1000),
            amount=pos.pop('position_initial_margin'),
            side=Side.LONG if pos['position_amt'] > .0 else Side.SHORT,
            quantity=abs(pos.pop('position_amt')),
            price=pos.pop('entry_price'),
            profit=pos.pop('unrealized_profit'),
            **pos,
        )


if __name__ == "__main__":
    BinancePosition.from_dict({
        "symbol": "BTCUSDT",
        "initialMargin": "0",
        "maintMargin": "0",
        "unrealizedProfit": "0.00000000",
        "positionInitialMargin": "0",
        "openOrderInitialMargin": "0",
        "leverage": "100",
        "isolated": "true",
        "entryPrice": "0.00000",
        "maxNotional": "250000",
        "bidNotional": "0",
        "askNotional": "0",
        "positionSide": "BOTH",
        "positionAmt": "0",
        "notional": "83.9089788",
        "isolatedWallet": "8.3932604",
        "updateTime": 0
    })

