import numpy as np

from trader.core.enumerate import OrderSide
from trader.core.model import Position
from trader.core.strategy import CallbackStrategy

from trader.backtest import BacktestFuturesBroker
from trader.core.model import Balance
from trader.data.model import Candles

from trader.ui.enumerate import Candlestick


def entry_logic(candles: Candles):
    return OrderSide.SELL, None


def exit_logic(candles: Candles, position: Position):
    return True


# Very simple strategy, just to see and check how exactly the backtesting framework works.
if __name__ == "__main__":
    asset = "USD"
    cash = 1000

    candles = Candles(
        candles=np.array([
            [1, 5, 7, 1, 8, 2],
            [2, 8, 9, 6, 6, 1],
            [3, 6, 8, 4, 5, 2],
        ]),
        symbol="XY",
        interval="1h",
        market="SPOT",
    )

    strategy = CallbackStrategy(
        broker=BacktestFuturesBroker(
            balance=Balance(asset=asset, free=cash),
            maker_fee_rate=0.0002,
            taker_fee_rate=0.0004,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=0.5,
        asset=asset,
        enter_position_callback=entry_logic,
        exit_position_callback=exit_logic,
    )

    strategy.run()
    strategy.plot(candlestick_type=Candlestick.JAPANESE)
