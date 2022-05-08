from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesTrader
from trader.backtest.model import BacktestBalance
from trader.core.enumerate import MA
from trader.core.indicator import DoubleMAIndicator
from trader.core.strategy import AutoIndicatorStrategy

from trader.ui.enumerate import Candlestick


"""
if __name__ == "__main__":

    dma = DoubleMAIndicator(fast_period=30, slow_period=50, fast_type=MA.EMA, slow_type=MA.EMA)

    run_backtest(
        broker="BINANCE",
        market="FUTURES",
        symbol="BTCUSDT",
        asset="USD",
        capital=1000,
        interval="15m",
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
        leverage=1,
        trade_ratio=0.5,
        indicators=[dma],
        entry_long_conditions=[dma.bullish_cross],
        entry_short_conditions=[dma.bearish_cross],
        exit_long_conditions=[dma.bearish_cross],
        exit_short_conditions=[dma.bullish_cross],
    )
"""


if __name__ == "__main__":

    start_cash = 1000
    asset = "USD"
    symbol = "BTCUSDT"

    candles = get_store_candles(
        symbol=symbol,
        interval="1h",
        market="FUTURES",
        storage_type=HDF5CandleStorage,
    )

    dma = DoubleMAIndicator(fast_period=30, slow_period=50, fast_type=MA.EMA, slow_type=MA.EMA)

    strategy = AutoIndicatorStrategy(
        trader=BacktestFuturesTrader(
            balance=BacktestBalance(asset=asset, free=start_cash),
            maker_fee_rate=0.0002,
            taker_fee_rate=0.0004,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=0.5,
        asset=asset,
        indicators=[dma],
        entry_long_conditions=[dma.bullish_cross],
        entry_short_conditions=[dma.bearish_cross],
        exit_long_conditions=[dma.bearish_cross],
        exit_short_conditions=[dma.bullish_cross],
    )

    strategy.run()
    strategy.plot_results(
        candlestick_type=Candlestick.LINE,
        custom_graphs=[dma],
    )
