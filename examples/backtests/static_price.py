from datetime import datetime

from trader.backtest import BacktestFuturesBroker
from trader.backtest.broker import Percentage

from trader.core.model import Balance, Position
from trader.core.strategy import Strategy
from trader.core.const import Side, Market

from trader.data.binance import get_store_candles, Interval
from trader.data.model import Symbol
from util.performance import measure_performance


class StaticPriceStrategy(Strategy):
    """
    Enters LONG if latest close price gets above 40.000.

    Enters SHORT if latest close price gets below 60.000.

    Closes LONG if latest close price is above 55.000.

    Closes SHORT if latest close price is below 40.000.
    """
    def __init__(self, *args, **kwargs):
        self.broker.set_leverage(symbol=symbol, leverage=1)

    def on_not_in_position(self):
        if self.candles.latest_close_price > 40_000 > self.candles.close_prices[-2]:
            self.broker.enter_position(
                symbol=symbol,
                side=Side.LONG,
                amount=1000,
            )
        elif self.candles.latest_close_price > 60_000 > self.candles.close_prices[-2]:
            self.broker.enter_position(
                symbol=symbol,
                side=Side.SHORT,
                amount=Percentage(100),
            )

    def on_in_position(self, position: Position):
        if position.side is Side.LONG and self.candles.latest_close_price > 55_000:
            self.broker.close_position_market(position.symbol)
        elif position.side is Side.SHORT and self.candles.latest_close_price < 40_000:
            self.broker.close_position_market(position.symbol)


if __name__ == '__main__':

    start_cash = 1000
    symbol = Symbol('BTC', 'USDT')

    candles = get_store_candles(
        symbol=symbol,
        interval=Interval.HOUR_1,
        market=Market.FUTURES,
    ).between(
        start=datetime(year=2021, month=1, day=1),
        end=datetime(year=2022, month=1, day=2)
    )

    broker = BacktestFuturesBroker(
        balances={symbol.quote: start_cash},
        symbol_leverage_pair={symbol: 1},
        maker_fee_percentage=0.2,
        taker_fee_percentage=0.4,
    )

    strategy = StaticPriceStrategy(candles=candles, broker=broker)

    strategy.run()
    strategy.plot()
