from typing import Iterable, Callable

from trader.core.model import Position
from trader.core.strategy import Strategy
from trader.data.model import Candles

from trader.core.const.trade_actions import SELL, BUY
from trader.core.enumerate import OrderSide, Mode
from trader.core.exception import TraderError
from trader.core.indicator import Indicator
from trader.core.interface import FuturesTrader


class AutoIndicatorStrategy(Strategy):

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

    def __update_indicators(self, candles: Candles):
        for ind in self.indicators:
            ind(candles)

    def __init__(
            self,
            trader: FuturesTrader,
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

        :param trader: Trader object.
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

        if trade_ratio <= 0 or trade_ratio >= 1:
            raise TraderError(f"trade_ratio must be between 0 and 1")

        super(AutoIndicatorStrategy, self).__init__(trader=trader, candles=candles)

        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.asset = asset
        self.indicators = indicators

        wrapper = self.__cached_results if self.mode == Mode.BACKTEST else self.__results
        self.__update_indicators(candles)

        self.entry_buy_conditions = wrapper(entry_long_conditions)
        self.entry_sell_conditions = wrapper(entry_short_conditions)
        self.exit_buy_conditions = wrapper(exit_long_conditions)
        self.exit_sell_conditions = wrapper(exit_short_conditions)

        self.entry_price = entry_price
        self.exit_price = exit_price
        self.profit_price = profit_price
        self.stop_price = stop_price

    def __enter_position(self, side: OrderSide):
        price = self.entry_price(self.candles, side)
        tp_price = self.profit_price(self.candles, side)
        sl_price = self.stop_price(self.candles, side)
        self.create_position(
            candles=self.candles,
            money=self.get_balance(self.asset).free * self.trade_ratio,
            leverage=self.leverage,
            side=side,
            price=price,
            profit_price=tp_price,
            stop_price=sl_price,
        )

    def __exit_position(self, position: Position):
        price = self.exit_price(self.candles, position)

        self.close_position(
            candles=self.candles,
            price=price,
        )

    def __call__(self, candles: Candles):
        if self.mode == Mode.LIVE:
            self.__update_indicators(candles)

        last_index = len(candles) - 1
        position = self.get_position(self.candles.symbol)

        if position is None:
            if self.entry_buy_conditions(last_index):
                self.__enter_position(OrderSide.BUY)
            elif self.entry_sell_conditions(last_index):
                self.__enter_position(OrderSide.SELL)
        else:
            if position.side == SELL and self.exit_buy_conditions(last_index):
                self.__exit_position(position)
            elif position.side == BUY and self.exit_sell_conditions(last_index):
                self.__exit_position(position)
