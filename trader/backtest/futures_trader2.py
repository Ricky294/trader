from typing import List, Optional

import numpy as np

from ..core.const.candle_index import CLOSE_PRICE_INDEX
from ..core.const.trade_actions import BUY, SELL
from ..core.interface import FuturesTrader
from ..core.model import Position, SymbolInfo, Order, Balance, LimitOrder, MarketOrder, StopMarketOrder, \
    TakeProfitMarketOrder
from ..core.util.trade import calculate_fee


class BacktestPosition:

    def __init__(
            self,
            entry_price: float,
            entry_side: int,
            entry_quantity: float,
    ):
        self.is_closed = False

        self.entry_money = entry_price * entry_quantity
        self.entry_price = entry_price
        self.entry_side = entry_side
        self.entry_quantity = entry_quantity

        self.exit_price = None
        self.exit_quantity = None

        self.__profit = 0

    def __call__(self, current_price: float):
        self.__latest_price = current_price

        if self.entry_side == BUY:
            self.__profit = current_price - self.entry_price * self.entry_quantity
        elif self.entry_side == SELL:
            self.__profit = self.entry_quantity - current_price * self.entry_quantity

    @classmethod
    def from_money(
            cls,
            entry_money: float,
            entry_price: float,
            entry_side: int,
    ):
        return cls(
            entry_quantity=entry_money / entry_price,
            entry_side=entry_side,
            entry_price=entry_price,
        )

    def close_position(self):
        if self.is_closed:
            raise Exception("Position is already closed.")

        self.is_closed = True
        self.exit_price = self.__latest_price
        self.exit_quantity = -self.entry_quantity

    def profit(self):
        return self.__profit


class BacktestFuturesTrader2:

    def __init__(
            self,
            balance: Balance,
            taker_fee_percentage: float,
            maker_fee_percentage: float,
            leverage=1,
    ):
        self._leverage = leverage

        self.taker_fee_percentage = taker_fee_percentage
        self.maker_fee_percentage = maker_fee_percentage

        self.balance = balance

        self.position: Optional[BacktestPosition] = None
        self.positions: List[BacktestPosition] = []

        self.limit_order: Optional[LimitOrder] = None
        self.market_order: Optional[MarketOrder] = None
        self.stop_order: Optional[StopMarketOrder] = None
        self.take_profit_order: Optional[TakeProfitMarketOrder] = None

    def __call__(self, candles: np.ndarray):
        latest_candle = candles[-1]
        latest_close = latest_candle[CLOSE_PRICE_INDEX]

        if self.position is not None:
            self.position(current_price=latest_close)

        if self.market_order is not None:
            money = self.__apply_fee(money=money, fee_percentage=self.taker_fee_percentage)

            self.position = BacktestPosition(
                entry_quantity=money,
                entry_price=,
                entry_side=self.market_order.side,
            )

    def cancel_orders(self, symbol: str) -> None:
        pass

    def __apply_fee(self, quantity: float, price: float, fee_percentage: float):
        fee = calculate_fee(money=money, fee_percentage=fee_percentage, leverage=self._leverage)
        self.balance.total -= fee
        self.balance.available -= fee
        return money - fee

    def __apply_fee(self, money: float, fee_percentage: float):
        fee = calculate_fee(money=money, fee_percentage=fee_percentage, leverage=self._leverage)
        self.balance.total -= fee
        self.balance.available -= fee
        return money - fee

    def create_position(
            self,
            symbol: str,
            side: int,
            money: float,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None
    ) -> None:
        s

    def close_position(self, symbol: str) -> None:
        self.position.close_position()
        self.__apply_fee(money=self.position.entry_money, fee_percentage=self.fee_percentage)
        self.positions.append(self.position)
        self.position = None

    def get_balances(self) -> List[Balance]:
        pass

    def get_balance(self, asset: str) -> Balance:
        pass

    def get_open_orders(self, symbol: str) -> List[Order]:
        pass

    def get_symbol_info(self, symbol: str) -> SymbolInfo:
        pass

    def get_position(self, symbol: str) -> Position:
        pass

    def set_leverage(self, symbol: str, leverage: int) -> None:
        pass

    def get_leverage(self, symbol) -> int:
        pass
