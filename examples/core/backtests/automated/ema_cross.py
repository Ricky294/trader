from datetime import datetime

from trader.core.model import Positions
from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesTrader
from trader.backtest.model import BacktestBalance
from trader.core.enumerate import MA
from trader.core.indicator import DoubleMAIndicator
from trader.core.strategy import AutoIndicatorStrategy
from trader.data.model.columnar import format_trade

from trader.ui.enumerate import Candlestick


if __name__ == "__main__":

    start_cash = 1000
    base_currency = "BTC"
    quote_currency = "USDT"

    candles = get_store_candles(
        base_currency=base_currency,
        quote_currency=quote_currency,
        interval="1d",
        market="FUTURES",
        storage_type=HDF5CandleStorage,
    )
    candles = candles.between(start=datetime(year=2020, month=1, day=1), end=datetime(year=2022, month=1, day=2))

    dma = DoubleMAIndicator(fast_period=20, slow_period=30, fast_type=MA.SMA, slow_type=MA.SMA)

    strategy = AutoIndicatorStrategy(
        trader=BacktestFuturesTrader(
            balance=BacktestBalance(time=candles.times[0], asset=quote_currency, free=start_cash),
            maker_fee_rate=0.0,
            taker_fee_rate=0.0,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=0.5,
        asset=quote_currency,
        indicators=[dma],
        entry_long_conditions=[dma.bullish_cross],
        entry_short_conditions=[dma.bearish_cross],
        exit_long_conditions=[dma.bearish_cross],
        exit_short_conditions=[dma.bullish_cross],
    )

    strategy.run()

    poses = Positions(strategy.trader.positions)

    format_trade(poses)

    x = 5

    strategy.plot(
        candlestick_type=Candlestick.JAPANESE,
        custom_graphs=[dma],
    )
