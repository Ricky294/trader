import numpy as np

from trader.backtest import BacktestFuturesTrader, BacktestBot
from trader.backtest.balance import BacktestBalance
from trader.core.indicator import Indicator
from trader.core.indicator.result import IndicatorResult
from trader.core.model.candles import Candles

from trader.core.const.trade_actions import SELL, BUY, NONE
from trader.core.enum import CandlestickType
from trader.core.strategy import Strategy


class TestEntryIndicator(Indicator):

    def __init__(self, *args, **data):
        self.buy_signal = np.array([1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0])
        self.sell_signal = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0])
        self.data = np.array([0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0])

    def __call__(self, candles: Candles) -> IndicatorResult:
        return IndicatorResult(
            self.buy_signal[:candles.shape[0]],
            self.sell_signal[:candles.shape[0]],
            data=self.data[:candles.shape[0]],
        )


class TestStrategy(Strategy):

    def __init__(
            self,
            symbol: str,
            trader: BacktestFuturesTrader,
            entry_indicator: Indicator,
            trade_ratio: float,
            leverage: int,
    ):
        super().__init__(trader=trader)
        self.entry_indicator = entry_indicator
        self.symbol = symbol
        self.trade_ratio = trade_ratio
        self.leverage = leverage

    def on_candle(self, candles: Candles):
        position = self.trader.get_position(self.symbol)

        result = self.entry_indicator(candles)
        signal = result.latest_signal()

        if position is None and signal is not NONE:
            latest_close = candles.latest_close_price

            stop_loss_price = (
                latest_close - 400 if signal == BUY else latest_close + 400
            )
            take_profit_price = (
                latest_close - 400 if signal == SELL else latest_close + 400
            )

            self.trader.create_position(
                symbol=self.symbol,
                money=self.trader.get_balance("USDT").free * self.trade_ratio,
                leverage=self.leverage,
                side=signal,
                take_profit_price=take_profit_price,
                stop_loss_price=stop_loss_price,
            )


def test_backtest_trading():
    from tests.backtest.test_candles import candles

    start_cash = 1000

    trader = BacktestFuturesTrader(
        balance=BacktestBalance(asset="USD", amount=start_cash),
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
    )
    strategy = TestStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1, entry_indicator=TestEntryIndicator())

    bot = BacktestBot()
    bot.add_data(candles=candles)
    bot.add_strategy(strategy=strategy)
    bot.run(candlestick_type=CandlestickType.JAPANESE)
