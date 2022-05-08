from __future__ import annotations

from typing import Iterable, Callable

from trader.data.model import Candles

from trader.core.model import Position
from trader.core.enumerate import OrderSide
from trader.core.exception import TraderException
from trader.core.interface import FuturesTrader

# Use this exact import in order to avoid circular import
from trader.core.strategy.managed_position import ManagedPositionStrategy


class AutoStrategy(ManagedPositionStrategy):

    def in_position(self, candles: Candles, position: Position):
        val = self.exit_price_callable(self.candles, position)

        if val:
            price = val if isinstance(val, float) else None
            self.close_position(
                symbol=candles.symbol,
                price=price,
            )

    def not_in_position(self, candles: Candles):
        side, price = self.entry_price_callable(self.candles)
        if side:
            tp = self.profit_price_callable(self.candles, side)
            sl = self.stop_price_callable(self.candles, side)
            self.create_position(
                symbol=candles.symbol,
                money=self.get_balance(self.asset).free * self.trade_ratio,
                leverage=self.leverage,
                side=side,
                price=price,
                profit_price=tp,
                stop_price=sl,
            )

    @staticmethod
    def __cached_results(functions: Iterable[Callable]):
        results = tuple(fun() for fun in functions)

        def wrapper(i):
            result_i = tuple(bool(res[i]) for res in results)
            return all(result_i)

        return wrapper

    @staticmethod
    def __results(functions: Iterable[Callable]):
        def wrapper(i):
            result_i = tuple(bool(fun()[i]) for fun in functions)
            return all(result_i)
        return wrapper

    def __init__(
            self,
            trader: FuturesTrader,
            candles: Candles,
            trade_ratio: float,
            leverage: int,
            asset: str,
            entry_price: Callable[[Candles], tuple[OrderSide | None, float | None]],
            exit_price: Callable[[Candles, Position], float | bool | None] = lambda _: False,
            profit_price: Callable[[Candles, OrderSide], float] = lambda _, __: None,
            stop_price: Callable[[Candles, OrderSide], float] = lambda _, __: None,
    ):
        """
        Creates an automated trading strategy. Enters and exits positions based on the callback conditions.
        Use logic callbacks to define entry/exit prices and stop loss/take profit prices on position entry.

        :param trader: Trader for backtest
        :param candles: Candles object, that contains candles data.
        :param trade_ratio: Float value between 0 and 1.
        :param leverage: Positive integer. Sets leverage.
        :param asset: Currency type to use when entering positions.
        :param entry_price: Enters position on side if OrderSide is returned.
        :param exit_price: Exits position if True is returned. (Optional)
        :param entry_price: Called on position entry. Expects entry side and current price and returns an entry price. (Optional)
        :param exit_price: Called on position exit. Expects entry side and current price and returns an exit price. (Optional)
        :param profit_price: Called on position entry. Expects entry side and current price and returns take profit price. (Optional)
        :param stop_price: Called on position entry. Expects entry side and current price and returns stop loss price. (Optional)

        Note: Exit conditions, take profit and stop loss price logic are optional, but you should define either
        the exit conditions or the take profit/stop loss logics in order to exit positions.
        """

        if trade_ratio <= 0 or trade_ratio >= 1:
            raise TraderException(f"trade_ratio must be between 0 and 1")

        super(AutoStrategy, self).__init__(trader=trader, candles=candles)

        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.asset = asset

        self.entry_price_callable = entry_price
        self.exit_price_callable = exit_price

        self.profit_price_callable = profit_price
        self.stop_price_callable = stop_price
