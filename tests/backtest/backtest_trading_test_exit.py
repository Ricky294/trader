from typing import List, Optional

from trader.backtest import BacktestFuturesTrader, BacktestBot, BacktestBalance
from trader.core.interface import FuturesTrader
from trader.core.model import Order, Position, Candles, Balance
from trader.core.const.trade_actions import SELL, BUY
from trader.core.enum import CandlestickType
from trader.core.strategy import ManagedSinglePositionStrategy


class TestExitStrategy(ManagedSinglePositionStrategy):

    def __init__(self, symbol: str, trader: FuturesTrader, trade_ratio: float, leverage: int):
        super().__init__(trader=trader, symbol=symbol)
        self.trade_ratio = trade_ratio
        self.leverage = leverage

    def on_entry_order(self, symbol: str, orders: List[Order]):
        self.logger.info(f"Created entry order(s): {', '.join((str(order) for order in orders))}")

    def on_close_order(self, symbol: str, order: Order):
        self.logger.info(f"Created close order: {order}")

    def on_set_leverage(self, symbol: str, leverage: int):
        self.logger.info(f"Leverage is set to: {leverage}")

    def on_cancel_orders(self, symbol: str, orders: List[Order]):
        self.logger.info(f"Canceled order(s): {', '.join((str(order) for order in orders))}")

    def on_get_balance(self, asset: str, balance: Optional[Balance]):
        self.logger.info(f"Balance: {balance}")

    def on_get_position(self, symbol: str, position: Optional[Position]):
        self.logger.info(f"Position: {position}")

    def in_position(self, candles: Candles, position: Position):
        is_bullish_candle = candles.is_bullish()

        if (position.side == SELL and is_bullish_candle) or (position.side == BUY and not is_bullish_candle):
            self.trader.close_position_market(self.symbol)

    def not_in_position(self, candles: Candles):
        signal = BUY if candles.is_bullish() else SELL
        self.trader.cancel_orders(self.symbol)
        self.trader.create_position(
            symbol=self.symbol,
            money=self.trader.get_balance("USD").free * self.trade_ratio,
            side=signal,
            leverage=self.leverage,
        )


def test_backtest_trading():
    from tests.backtest.test_candles import candles

    start_cash = 1000

    trader = BacktestFuturesTrader(
        balance=BacktestBalance(asset="USD", amount=start_cash),
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
    )
    strategy = TestExitStrategy("XYZ", trader=trader, trade_ratio=0.5, leverage=1)

    bot = BacktestBot()
    bot.add_data(candles=candles)
    bot.add_strategy(strategy=strategy)
    bot.run(enable_logging=True)
    bot.plot(candlestick_type=CandlestickType.JAPANESE)
