# nopycln: file

from .futures_trader import BacktestFuturesTrader
from .tape import ArrayTape
from .position import BacktestPosition
from .order_group import BacktestOrderGroup
from .exception import NotEnoughFundsError
from .backtester import run_backtest
from .custom_graph import CustomGraph
from .trade_figure import TradeResultFigure
from .bot import BacktestBot, backtest_multiple_bot, BacktestRunParams
from .balance import BacktestBalance
from .indicator_optimizer import OptimizedIndicator

import logging


BACKTEST_LOGGER = "trader.backtest"

logger = logging.getLogger(name=BACKTEST_LOGGER)
if not logger.handlers:
    logger.propagate = False
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(fmt="%(levelname)s-%(name)s: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=logging.INFO)

    stream_handler.setFormatter(fmt=formatter)
    logger.addHandler(stream_handler)
