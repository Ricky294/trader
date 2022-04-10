from __future__ import annotations

from trader_data.core.model import Candles

from trader.core.exception import PositionError
from trader.core.model import Position, LimitOrder, MarketOrder, Order
from trader.core.const.trade_actions import BUY, SELL
from trader.core.util.trade import calculate_money_fee

from .balance import BacktestBalance
from .exception import LiquidationError


class BacktestPosition(Position):

    __slots__ = "entry_time", "entry_fee", "exit_fee", "exit_time", "exit_price", "__candles"

    def __init__(
            self,
            order: MarketOrder | LimitOrder,
            candles: Candles,
            balance: BacktestBalance,
            leverage: int,
            taker_fee_rate: float,
            maker_fee_rate: float,
    ):

        fee = calculate_money_fee(
            money=order.money,
            fee_rate=taker_fee_rate if order.is_taker() else maker_fee_rate,
            leverage=leverage
        )
        balance.free -= fee
        order.money -= fee

        super().__init__(
            symbol=order.symbol,
            side=order.side,
            entry_time=int(candles.latest_open_time),
            entry_price=candles.latest_close_price if order.is_taker() else order.price,
            money=order.money,
            leverage=leverage,
        )
        self.entry_fee = fee
        self.__candles = candles

        self.exit_fee: int | None = None
        self.exit_time: int | None = None
        self.exit_price: float | None = None

    def __call__(self, balance: BacktestBalance, candles: Candles):
        if self.is_closed():
            return

        self.__candles = candles

        profit = self._profit(candles.latest_low_price if self.side == BUY else candles.latest_high_price)

        if profit < 0 and abs(profit) >= balance.free:
            raise LiquidationError(f"Position liquidated! Position loss at liquidation: {profit}.")

    def __eq__(self, other):
        return (
                isinstance(other, type(self))
                and (self.symbol, self.entry_time, self.side)
                == (other.symbol, other.entry_time, other.side)
        )

    def __hash__(self):
        return hash((self.symbol, self.entry_time, self.side))

    def is_closed(self):
        return self.exit_time is not None

    def close(
            self,
            time: int,
            price: float,
            order: Order,
            balance: BacktestBalance,
            maker_fee_rate: float,
            taker_fee_rate: float,
            leverage: int,
    ):
        fee = calculate_money_fee(
            money=self._money,
            fee_rate=taker_fee_rate if order.is_taker() else maker_fee_rate,
            leverage=leverage
        )

        self.exit_fee = fee
        self.exit_time = time
        self.exit_price = price

        balance.free -= fee
        balance.free += self._profit(price)

    def profit(self):
        price = self.__candles.latest_close_price if self.exit_price is None else self.exit_price
        return self._profit(price)

    def _profit(self, price: float):
        if self.side == BUY:
            ret = price / self.entry_price * self._money - self._money
        elif self.side == SELL:
            ret = self.entry_price / price * self._money - self._money
        else:
            raise PositionError(f"'side' must be {BUY} or {SELL}.")

        return ret * self.leverage
