# nopycln: file

from .base import Strategy
from .single_position import SinglePositionStrategy

BACKTEST_STRATEGY_LOGGER = "trader.backtest.strategy"
LIVE_STRATEGY_LOGGER = "trader.live.strategy"
