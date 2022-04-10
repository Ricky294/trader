from trader_data.binance import get_store_binance_candles
from trader_data.core.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesTrader, BacktestBalance
from trader.core.enum import Candlestick, MA
from trader.core.indicator import DoubleMAIndicator
from trader.core.strategy import AutoStrategy


if __name__ == "__main__":

    start_cash = 1000
    asset = "USD"
    symbol = "BTCUSDT"

    dma = DoubleMAIndicator(fast_period=30, slow_period=50, fast_type=MA.EMA, slow_type=MA.EMA)

    candles = get_store_binance_candles(
        symbol=symbol,
        interval="15m",
        market="FUTURES",
        storage_type=HDF5CandleStorage,
    )

    strategy = AutoStrategy(
        symbol=symbol,
        trader=BacktestFuturesTrader(
            balance=BacktestBalance(asset=asset, amount=start_cash),
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
    strategy.plot_backtest(
        candlestick_type=Candlestick.LINE,
        custom_graphs=[dma],
    )
