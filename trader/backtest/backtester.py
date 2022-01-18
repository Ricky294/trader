import numpy as np
from tqdm import tqdm

from trader.core.strategy import Strategy

from .futures_trader import BacktestFuturesTrader
from .log import logger


def run_backtest(
    candles: np.ndarray,
    strategy: Strategy,
):
    if not isinstance(strategy.trader, BacktestFuturesTrader):
        raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

    logger.info(f"Running backtest on {len(candles)} candles.")
    for i in tqdm(range(1, len(candles))):
        candles_head = candles[:i]
        strategy(candles_head)
        strategy.trader(candles_head)

    logger.info(
        f"Finished. Entered {len(strategy.trader.positions)} positions. "
        f"Final balance: {strategy.trader.balance.total:.3f}"
    )
