import numpy as np

from trader.backtest import BacktestFuturesTrader, run_backtest
from trader.backtest.plotter import plot_backtest_results

from trader.core.model import Balance
from trader.core.const.trade_actions import SELL, BUY
from trader.core.const.candle_index import OPEN_PRICE_INDEX, CLOSE_PRICE_INDEX
from trader.core.enum import CandlestickType
from trader.core.strategy import Strategy
from trader.core.util.trade import calculate_quantity


start_cash = 1000

candles = np.array([
    # open_time, open_price, high_price, low_price, close_price, volume
    [1640991600, 950, 1100, 900, 1000, 100],
    [1640991660, 1000, 1200, 800, 900, 100],
    [1640991720, 900, 1000, 800, 850, 100],
    [1640991780, 850, 1100, 500, 900, 100],
    [1640991840, 900, 1100, 700, 1000, 100],
    [1640991900, 700, 800, 600, 620, 100],
    [1640991960, 620, 1200, 400, 1000, 100],
    [1640992020, 1000, 1500, 950, 1400, 100],
    [1640992080, 1400, 1600, 1100, 1500, 100],
    [1640992140, 1500, 1800, 1200, 1600, 100],
    [1640992200, 1600, 2200, 1550, 1800, 100],
    [1640992260, 1800, 1900, 1400, 1450, 100],
    [1640992320, 1450, 1500, 900, 1000, 100],
    [1640992380, 1000, 1200, 950, 1100, 100],
    [1640992440, 1100, 1150, 800, 900, 100],
], dtype=np.float)


class TestStrategy(Strategy):

    def __init__(self, symbol: str, trader: BacktestFuturesTrader, trade_ratio: float):
        super().__init__(trader=trader)
        self.symbol = symbol
        self.trade_ratio = trade_ratio

    def on_candle(self, candles: np.ndarray):
        latest_candle = candles[-1]
        latest_close = latest_candle[CLOSE_PRICE_INDEX]
        position = self.trader.get_position(self.symbol)
        is_bullish_candle = latest_candle[CLOSE_PRICE_INDEX] > latest_candle[OPEN_PRICE_INDEX]

        if position is None:
            if is_bullish_candle:
                signal = BUY
            else:
                signal = SELL

            quantity = calculate_quantity(
                trade_ratio=self.trade_ratio,
                balance=self.trader.get_balance("USDT").total,
                side=signal,
                price=latest_close,
            )

            self.trader.create_position(
                symbol=self.symbol,
                quantity=quantity,
            )
        else:
            if (position.side == SELL and is_bullish_candle) or (position.side == BUY and not is_bullish_candle):
                self.trader.close_position(self.symbol)


def test_backtest_trading():

    trader = BacktestFuturesTrader(
        interval="1m",
        symbol="BTCUSDT",
        balance=Balance("USDT", total=start_cash, available=start_cash),
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
        leverage=1,
    )
    strategy = TestStrategy("XYZ", trader=trader, trade_ratio=0.5)

    run_backtest(
        candles=candles,
        strategy=strategy
    )

    plot_backtest_results(
        candles=candles.T,
        trader=trader,
        start_cash=start_cash,
        candlestick_type=CandlestickType.JAPANESE,
    )
