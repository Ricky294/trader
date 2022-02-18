from trader.backtest import BacktestFuturesTrader, BacktestBot
from trader.backtest.balance import BacktestBalance
from trader.core.model import Position
from trader.core.model.candles import Candles

from trader.core.const.trade_actions import SELL, BUY
from trader.core.enum import CandlestickType
from trader.core.strategy import SinglePositionStrategy


class TestStrategy(SinglePositionStrategy):

    def __init__(self, symbol: str, trader: BacktestFuturesTrader, trade_ratio: float, leverage: int):
        super().__init__(symbol=symbol, trader=trader)
        self.trade_ratio = trade_ratio
        self.leverage = leverage
        self.trader.set_leverage(symbol=symbol, leverage=leverage)

    def on_next(self, candles: Candles, position: Position):
        is_bullish_candle = candles.is_bullish()

        if is_bullish_candle:
            signal = BUY
        else:
            signal = SELL

        if self.trader.get_position(self.symbol) is None:
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
    strategy = TestStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1)

    bot = BacktestBot()
    bot.add_data(candles=candles)
    bot.add_strategy(strategy=strategy)

    bot.run(candlestick_type=CandlestickType.JAPANESE)
