from tests.backtest.backtest_trading_test_exit import TestStrategy as ExitTestStrategy
from tests.backtest.backtest_trading_test_sl_tp import TestStrategy as SLTPTestStrategy
from tests.backtest.test_candles import candles

from trader.backtest import (
    BacktestFuturesTrader,
    BacktestBot,
    backtest_multiple_bot,
    BacktestRunParams,
    BacktestBalance
)
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

    bot1 = BacktestBot(
        candles=candles,
        strategy=exit_strategy,
    )

    bot2 = BacktestBot(
        candles=candles,
        strategy=sltp_strategy,
    )

    backtest_multiple_bot(
        bots=[bot1, bot2],
        params_list=[
            BacktestRunParams(candlestick_type=CandlestickType.JAPANESE),
            BacktestRunParams(candlestick_type=CandlestickType.JAPANESE),
        ]
    )
