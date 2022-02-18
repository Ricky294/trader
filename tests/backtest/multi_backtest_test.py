from tests.backtest.backtest_trading_test_exit import TestExitStrategy as ExitTestStrategy
from tests.backtest.backtest_trading_test_sl_tp import TestStrategy as SLTPTestStrategy
from tests.backtest.test_candles import candles

from trader.backtest import (
    BacktestFuturesTrader,
    BacktestBot,
    backtest_multiple_bot,
    BacktestRunParams,
    BacktestBalance,
)
from trader.backtest.bot import BacktestPlotParams
from trader.core.enum import CandlestickType


def test_multiple_bot_backtest():
    start_cash = 1000

    trader = BacktestFuturesTrader(
        balance=BacktestBalance(asset="USD", amount=start_cash),
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
    )
    exit_strategy = ExitTestStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1)
    sltp_strategy = SLTPTestStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1)

    bot1 = BacktestBot()
    bot1.add_data(candles)
    bot1.add_strategy(exit_strategy)

    bot2 = BacktestBot()
    bot2.add_data(candles)
    bot2.add_strategy(sltp_strategy)

    backtest_multiple_bot(
        bots=[bot1, bot2],
        run_params=[
            BacktestRunParams(),
            BacktestRunParams(),
        ],
        plot_params=[
            BacktestPlotParams(candlestick_type=CandlestickType.JAPANESE),
            BacktestPlotParams(candlestick_type=CandlestickType.JAPANESE)
        ],
    )
