from typing import Iterable, Callable

import trader.core.strategy.vector as strategy

from trader.core.indicator import Indicator
from trader.core.interface import FuturesBroker
from trader.core.model import Position, Balance
from trader.core.super_enum import Mode, OrderSide

from trader.data.model import Candles


class IndicatorStrategy(strategy.VectorStrategy):

    def _update_indicators(self, candles: Candles):
        for ind in self.indicators:
            ind(candles)

    def __init__(
            self,
            broker: FuturesBroker,
            candles: Candles,
            trade_ratio: float,
            leverage: int,
            asset: str,
            indicators: Iterable[Indicator],
            entry_long_conditions: Iterable[Callable[[], Iterable]],
            entry_short_conditions: Iterable[Callable[[], Iterable]],
            exit_long_conditions: Iterable[Callable[[], Iterable]] = (),
            exit_short_conditions: Iterable[Callable[[], Iterable]] = (),
            entry_price: Callable[[Candles, OrderSide], float] = lambda _, __: None,
            profit_price: Callable[[Candles, OrderSide], float] = lambda _, __: None,
            stop_price: Callable[[Candles, OrderSide], float] = lambda _, __: None,
            exit_price: Callable[[Candles, Position], float] = lambda _, __: None,
    ):
        """
        Creates an automated trading strategy. Enters and exits positions based on the condition callbacks.
        Use price callbacks to define entry/exit and stop loss/take profit prices on position entry.

        :param broker: Trader object.
        :param candles: Candle data.
        :param trade_ratio: Defines the position size per trade (between 0 and 1).
        :param leverage: Sets leverage (positive integer).
        :param asset: Asset balance to spend when entering positions.
        :param indicators: Used trading indicators on this strategy.
        :param entry_long_conditions: Indicator callback(s) with no input. Long entry signals.
        :param entry_short_conditions: Indicator callback(s) with no input. Short entry signals.
        :param exit_long_conditions: Indicator callback(s) with no input. Long position exit signals. (Optional)
        :param exit_short_conditions: Indicator callback(s) with no input. Short position exit signals. (Optional)
        :param entry_price: Defines position entry price. Called on position entry. (Optional)
        :param profit_price: Defines take profit price. Called on position entry. (Optional)
        :param stop_price: Defines stop loss price. Called on position entry. (Optional)
        :param exit_price: Defines position exit price. Called on position close. (Optional)
        :raises TraderError: If trade ratio is not between 0 and 1.

        Note: Exit conditions, take profit and stop loss price logic are optional, but you should define either
        the exit conditions or the take profit/stop loss logics in order to exit positions.
        """

        self.indicators = indicators
        self._update_indicators(candles)

        super().__init__(
            broker=broker,
            candles=candles,
            asset=asset,
            leverage=leverage,
            trade_ratio=trade_ratio,
            entry_long_conditions=entry_long_conditions,
            entry_short_conditions=entry_short_conditions,
            exit_long_conditions=exit_long_conditions,
            exit_short_conditions=exit_short_conditions,
            entry_price=entry_price,
            profit_price=profit_price,
            stop_price=stop_price,
            exit_price=exit_price,
        )

    def in_position(self, candles: Candles, position: Position, *args, **kwargs):
        if self.mode == Mode.LIVE:
            self._update_indicators(candles)
        super().in_position(candles=candles, position=position, *args, **kwargs)

    def not_in_position(self, candles: Candles, balance: Balance, *args, **kwargs):
        super().not_in_position(candles=candles, balance=balance, *args, **kwargs)
