from __future__ import annotations

from typing import Callable, TypeVar

from trader.data.model import Candles

from trader.core.model import Position, Balance, Order
from trader.core.enumerate import OrderSide
from trader.core.exception import TraderError
from trader.core.interface import FuturesBroker

# Use this exact import in order to avoid circular import
from trader.core.strategy.managed_position import ManagedPositionStrategy


Price = TypeVar('Price', bound=float)


class CallbackStrategy(ManagedPositionStrategy):

    def __init__(
            self,
            broker: FuturesBroker,
            candles: Candles,
            trade_ratio: float,
            leverage: int,
            asset: str,
            enter_position_callback: Callable[[Candles, Balance, list[Order]], tuple[OrderSide, Price] | OrderSide | None],
            take_profit_callback: Callable[[Candles, Balance, list[Order], OrderSide], Price] = lambda *args, **kwargs: None,
            stop_loss_callback: Callable[[Candles, Balance, list[Order], OrderSide], Price] = lambda *args, **kwargs: None,
            exit_position_callback: Callable[[Candles, Balance, list[Order], Position], Price | bool | None] = lambda *args, **kwargs: False,
    ):
        """
        Creates an automated trading strategy. Enters and exits positions based on the callback conditions.
        Use logic callbacks to define entry/exit prices and stop loss/take profit prices on position entry.

        :param broker: Trader for backtest
        :param candles: Candles object, that contains candles data.
        :param trade_ratio: Float value between 0 and 1.
        :param leverage: Positive integer. Sets leverage.
        :param asset: Currency type to use when entering positions.
        :param enter_position_callback: Called on position entry. Expects entry side and current price and returns an entry price. (Optional)
        :param exit_position_callback: Called on position exit. Expects entry side and current price and returns an exit price. (Optional)
        :param take_profit_callback: Called on position entry. Expects entry side and current price and returns take profit price. (Optional)
        :param stop_loss_callback: Called on position entry. Expects entry side and current price and returns stop loss price. (Optional)

        Note: Exit conditions, take profit and stop loss price logic are optional, but you should define either
        the exit conditions or the take profit/stop loss logics in order to exit positions.
        """

        if trade_ratio < 0 or trade_ratio > 1:
            raise TraderError(f"trade_ratio must be between 0 and 1")

        super(CallbackStrategy, self).__init__(broker=broker, candles=candles, asset=asset)

        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.asset = asset

        self.entry_callback = enter_position_callback
        self.exit_position_callback = exit_position_callback

        self.take_profit_callback = take_profit_callback
        self.stop_loss_callback = stop_loss_callback

    def in_position(self, candles: Candles, balance: Balance, open_order: list[Order], position: Position):
        ret = self.exit_position_callback(candles, balance, open_order, position)

        if ret is True:
            self.broker.close_position()
        elif ret is float:
            self.broker.close_position(ret)

    def not_in_position(self, candles: Candles, balance: Balance, open_order: list[Order]):
        ret = self.entry_callback(candles, balance, open_order)
        if ret:
            if isinstance(ret, tuple):
                side, price = ret
            else:
                side = ret
                price = None

            tp = self.take_profit_callback(candles, balance, open_order, side)
            sl = self.stop_loss_callback(candles, balance, open_order, side)
            self.broker.enter_position(
                symbol=candles.symbol,
                amount=self.broker.get_balance(self.asset).free * self.trade_ratio,
                leverage=self.leverage,
                asset=self.asset,
                side=side,
                price=price,
                profit_price=tp,
                stop_price=sl,
            )
