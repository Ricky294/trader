from datetime import datetime

from trader.backtest import BacktestFuturesBroker

from trader.core.model import Balance, Order
from trader.core.strategy import Strategy
from trader.core.const import Side, OrderType, Market

from trader.data.binance import get_store_candles, Interval
from trader.data.model import Symbol
from trader.ui.const import Candlestick


class TrailingStopStrategy(Strategy):
    """
    Enters LONG if latest close price gets above 40.000.

    Enters SHORT if latest close price gets below 60.000.

    Closes LONG if latest close price is above 55.000.

    Closes SHORT if latest close price is below 40.000.
    """

    def on_not_in_position(self):
        if self.candles.latest_close_price > 40_000 > self.candles.close_prices[-2]:
            order = Order.market(
                symbol=symbol,
                side=Side.LONG,
                amount=100,
            )
            self.broker.create_order(order)

            ts_order = Order.trailing_stop_market_order(
                symbol=symbol,
                side=Side.SELL,
                trailing_rate=2,
                amount=100,
            )
            self.broker.create_order(ts_order)
        elif self.candles.latest_close_price > 60_000 > self.candles.close_prices[-2]:
            order = Order(
                symbol=symbol,
                side=Side.SHORT,
                type=OrderType.MARKET,
                amount=100,
            )
            self.broker.create_order(order)

            ts_order = Order.trailing_stop_market_order(
                symbol=symbol,
                side=Side.BUY,
                trailing_percentage=2,
                amount=100,
            )
            self.broker.create_order(ts_order)


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
        maker_fee_percentage=0.02,
        taker_fee_percentage=0.04,
    )

    strategy = TrailingStopStrategy(candles=candles, broker=broker)
    strategy.run()
    strategy.plot(
        candlestick_type=Candlestick.JAPANESE,
    )
