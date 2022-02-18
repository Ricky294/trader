from abc import abstractmethod
from typing import List, Optional

from trader.core.const.trade_actions import NONE, BUY, SELL
from trader.core.exception import PositionError
from trader.core.interface import FuturesTrader
from trader.core.model import Candles, Position
from trader.core.strategy import SinglePositionStrategy
from trader.core.indicator import Indicator


class EntryExitIndicatorStrategy(SinglePositionStrategy):

    def __init__(
            self,
            symbol: str,
            trader: FuturesTrader,
            entry_indicators: List[Indicator],
            exit_indicators: List[Indicator],
            **kwargs,
    ):
        if len(entry_indicators) == 0:
            raise PositionError("NO ENTRY INDICATOR(S)! THIS STRATEGY WILL NEVER OPEN A POSITION!")

        if len(exit_indicators) == 0:
            raise PositionError("NO EXIT INDICATOR(S)! THIS STRATEGY WILL NEVER CLOSE A POSITION!")

        super(EntryExitIndicatorStrategy, self).__init__(symbol, trader, **kwargs)
        self.entry_indicators = entry_indicators
        self.exit_indicators = exit_indicators

    @staticmethod
    def _aggregate_signal(candles: Candles, indicators: List[Indicator]):
        for indicator in indicators:
            indicator(candles)

        signals = tuple(indicator.latest_signal() for indicator in indicators)
        if all((signal == BUY for signal in signals)):
            return BUY
        elif all((signal == SELL for signal in signals)):
            return SELL
        return NONE

    def on_next(self, candles: Candles, position: Optional[Position]):
        if position is None:
            self.not_in_position(candles, self._aggregate_signal(candles, self.entry_indicators))
        else:
            self.in_position(candles, position, self._aggregate_signal(candles, self.exit_indicators))

    @abstractmethod
    def in_position(self, candles: Candles, position: Position, exit_signal: int):
        pass

    @abstractmethod
    def not_in_position(self, candles: Candles, entry_signal: int):
        pass
