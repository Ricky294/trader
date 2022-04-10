from typing import Iterable, Callable

from trader_data.core.model import Candles

from trader.core.const.trade_actions import SELL, BUY
from trader.core.enum import OrderSide, Mode
from trader.core.exception import TraderException
from trader.core.indicator import Indicator
from trader.core.interface import FuturesTrader
from trader.core.strategy import Strategy


class AutoStrategy(Strategy):

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
            symbol: str,
            trade_ratio: float,
            leverage: int,
            asset: str,
            indicators: Iterable[Indicator],
            entry_long_conditions: Iterable[Callable[[], Iterable]],
            entry_short_conditions: Iterable[Callable[[], Iterable]],
            exit_long_conditions: Iterable[Callable[[], Iterable]] = (),
            exit_short_conditions: Iterable[Callable[[], Iterable]] = (),
            entry_price_logic: Callable[[OrderSide, float], float] = lambda _, __: None,
            exit_price_logic: Callable[[OrderSide, float], float] = lambda _, __: None,
            take_profit_price_logic: Callable[[OrderSide, float], float] = lambda _, __: None,
            stop_loss_price_logic: Callable[[OrderSide, float], float] = lambda _, __: None,
    ):
        """
        Creates an automated trading strategy. Enters and exits positions based on the callback conditions.
        Use logic callbacks to define entry/exit prices and stop loss/take profit prices on position entry.

        :param trader: Trader for backtest
        :param candles: Candles object, that contains candles data.
        :param symbol: Traded symbol.
        :param trade_ratio: Float value between 0 and 1.
        :param leverage: Positive integer. Sets leverage.
        :param asset: Currency type to use when entering positions.
        :param indicators: Used trading indicators on this strategy.
        :param entry_long_conditions: Indicator callback(s) with no input params signaling long position entries.
        :param entry_short_conditions: Indicator callback(s) with no input params signaling short position entries.
        :param exit_long_conditions: Indicator callback(s) with no input params signaling long position exits. (Optional)
        :param exit_short_conditions: Indicator callback(s) with no input params signaling short position exits. (Optional)
        :param entry_price_logic: Called on position entry. Expects entry side and current price and returns an entry price. (Optional)
        :param exit_price_logic: Called on position exit. Expects entry side and current price and returns an exit price. (Optional)
        :param take_profit_price_logic: Called on position entry. Expects entry side and current price and returns take profit price. (Optional)
        :param stop_loss_price_logic: Called on position entry. Expects entry side and current price and returns stop loss price. (Optional)

        Note: Exit conditions, take profit and stop loss price logic are optional, but you should define either
        the exit conditions or the take profit/stop loss logics in order to exit positions.
        """

        if trade_ratio <= 0 or trade_ratio >= 1:
            raise TraderException(f"trade_ratio must be between 0 and 1")

        super(AutoStrategy, self).__init__(trader=trader, candles=candles)

        self.trader = trader
        self.symbol = symbol
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

        self.entry_price_logic = entry_price_logic
        self.close_price_logic = exit_price_logic
        self.take_profit_price_logic = take_profit_price_logic
        self.stop_loss_price_logic = stop_loss_price_logic

    def __create_position(self, side: OrderSide):
        current_price = self.get_latest_price(self.symbol)

        price = self.entry_price_logic(side, current_price)
        tp = self.take_profit_price_logic(side, current_price)
        sl = self.stop_loss_price_logic(side, current_price)
        self.create_position(
            symbol=self.symbol,
            money=self.get_balance(self.asset).free * self.trade_ratio,
            leverage=self.leverage,
            side=side,
            price=price,
            take_profit_price=tp,
            stop_loss_price=sl,
        )

    def __close_position(self, side: OrderSide):
        current_price = self.get_latest_price(self.symbol)
        price = self.close_price_logic(side, current_price)

        self.close_position(
            symbol=self.symbol,
            price=price,
        )

    def __call__(self, candles: Candles):
        def enter_exit_position():
            last_index = len(candles) - 1
            position = self.get_position(self.symbol)

            if position is None:
                if self.entry_buy_conditions(last_index):
                    self.__create_position(OrderSide.BUY)
                elif self.entry_sell_conditions(last_index):
                    self.__create_position(OrderSide.SELL)
            else:
                if position.side == SELL and self.exit_buy_conditions(last_index):
                    self.__close_position(OrderSide.BUY)
                elif position.side == BUY and self.exit_sell_conditions(last_index):
                    self.__close_position(OrderSide.SELL)

        if self.mode == Mode.BACKTEST:
            enter_exit_position()
        else:
            self.__update_indicators(candles)
            enter_exit_position()
