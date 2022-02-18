# nopycln: file

from .base import Strategy
from .single_position import SinglePositionStrategy, ManagedSinglePositionStrategy
from .multi_position import MultiPositionStrategy
from .indicator_strategy import EntryExitIndicatorStrategy

BACKTEST_STRATEGY_LOGGER = "trader.backtest.strategy"
LIVE_STRATEGY_LOGGER = "trader.live.strategy"
