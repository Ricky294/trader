from trader.backtest import BacktestFuturesTrader, BacktestBot
from trader.backtest.balance import BacktestBalance
from trader.core.model.candles import Candles

from trader.core.const.trade_actions import SELL, BUY
from trader.core.enum import CandlestickType
from trader.core.strategy import Strategy


class TestStrategy(Strategy):

    def __init__(self, symbol: str, trader: BacktestFuturesTrader, trade_ratio: float, leverage: int):
        super().__init__(trader=trader)
        self.symbol = symbol
        self.trade_ratio = trade_ratio
        self.leverage = leverage

    def on_candle(self, candles: Candles):
        position = self.trader.get_position(self.symbol)

        is_bullish_candle = candles.is_bullish()
        if position is None:
            if is_bullish_candle:
                signal = BUY
            else:
                signal = SELL

            self.trader.create_position(
                symbol=self.symbol,
                money=self.trader.get_balance("USDT").free * self.trade_ratio,
                side=signal,
                leverage=self.leverage,
            )
        else:
            if (position.side == SELL and is_bullish_candle) or (position.side == BUY and not is_bullish_candle):
                self.trader.close_position_market(self.symbol)


def test_backtest_trading():
    from tests.backtest.test_candles import candles

    start_cash = 1000

    trader = BacktestFuturesTrader(
        balance=BacktestBalance(asset="USD", amount=start_cash),
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
    )
    strategy = TestStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1)

    bot = BacktestBot()
    bot.add_data(candles=candles)
    bot.add_strategy(strategy=strategy)
    bot.run(candlestick_type=CandlestickType.JAPANESE)
