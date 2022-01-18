import numpy as np

from trader.backtest import BacktestFuturesTrader, run_backtest, positions_to_array
from trader.backtest.transform_positions import add_or_reduce_positions_to_array
from trader.backtest.plotter import plot_backtest_results

from trader.core.model import SymbolInfo, Balance
from trader.core.const.trade_actions import SELL, BUY
from trader.core.const.candle_index import OPEN_PRICE_INDEX, CLOSE_PRICE_INDEX
from trader.core.enum import CandlestickType
from trader.core.strategy import Strategy
from trader.core.util.trade import calculate_quantity


class TestStrategy(Strategy):

    def __init__(self, symbol: str, trader: BacktestFuturesTrader, trade_ratio: float):
        super().__init__(trader=trader)
        self.symbol = symbol
        self.trade_ratio = trade_ratio

    def on_candle(self, candles: np.ndarray):
        latest_candle = candles[-1]
        is_bullish_candle = latest_candle[CLOSE_PRICE_INDEX] > latest_candle[OPEN_PRICE_INDEX]

        if is_bullish_candle:
            signal = BUY
        else:
            signal = SELL

        if self.trader.get_position(self.symbol) is None:
            latest_close = latest_candle[CLOSE_PRICE_INDEX]
            quantity = calculate_quantity(
                trade_ratio=self.trade_ratio,
                balance=self.trader.get_balance("USDT").total,
                side=signal,
                price=latest_close,
            )

            stop_loss_price = (
                latest_close - 400 if signal == BUY else latest_close + 400
            )
            take_profit_price = (
                latest_close - 400 if signal == SELL else latest_close + 400
            )

            self.trader.create_position(
                symbol=self.symbol,
                quantity=quantity,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
            )


def test_backtest_trading():
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

    trader = BacktestFuturesTrader(
        interval="1m",
        symbol_info=SymbolInfo(symbol="BTCUSDT", quantity_precision=3, price_precision=2),
        balance=Balance("USDT", total=start_cash, available=start_cash),
        fee_ratio=0,
        leverage=10,
    )
    strategy = TestStrategy("XYZ", trader=trader, trade_ratio=0.01)

    run_backtest(
        candles=candles,
        strategy=strategy
    )

    plot_backtest_results(
        candles=candles.T,
        positions=positions_to_array(trader.positions),
        add_or_reduce_positions=add_or_reduce_positions_to_array(trader.positions),
        start_cash=start_cash,
        candlestick_type=CandlestickType.JAPANESE,
    )

