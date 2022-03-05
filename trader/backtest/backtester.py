import logging

from tqdm import tqdm

from trader import MONEY_PRECISION
from trader.backtest import BacktestFuturesTrader
from trader.core.strategy import Strategy
from trader.core.model.candles import Candles


def run_backtest(
    candles: Candles,
    strategy: Strategy,
):
    from . import BACKTEST_LOGGER
    if not isinstance(strategy.trader, BacktestFuturesTrader):
        raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

    candle_wrapper = Candles()
    logging.getLogger(BACKTEST_LOGGER).info(f"Running backtest on {len(candles)} candles.")
    for i in tqdm(range(len(candles))):
        candles_head = candles[:i+1]
        candle_wrapper.next(candles_head)
        strategy(candle_wrapper)
        strategy.trader(candle_wrapper)

    logging.getLogger(BACKTEST_LOGGER).info(
        f"Finished. Entered {len(strategy.trader.positions)} positions. "
        f"Final balance: {strategy.trader.balance.free:.{MONEY_PRECISION}f}"
    )
