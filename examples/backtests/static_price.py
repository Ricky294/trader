from datetime import datetime

from trader.backtest import BacktestFuturesBroker

from trader.core.model import Balance, Position, Order
from trader.core.strategy import Strategy
from trader.core.const import Side, OrderType, Market

from trader.data.binance import get_store_candles, Interval


class StaticPriceStrategy(Strategy):
    """
    Enters LONG if latest close price gets above 40.000.

    Enters SHORT if latest close price gets below 60.000.

    Closes LONG if latest close price is above 55.000.

    Closes SHORT if latest close price is below 40.000.
    """

    def on_not_in_position(self):
        if self.candles.latest_close_price > 40_000 > self.candles.close_prices[-2]:
            order = Order(
                symbol=symbol,
                side=Side.LONG,
                type=OrderType.MARKET,
                amount=1000,
            )
            self.broker.create_order(order)
        elif self.candles.latest_close_price > 60_000 > self.candles.close_prices[-2]:
            order = Order(
                symbol=symbol,
                side=Side.SHORT,
                type=OrderType.MARKET,
                amount=100,
            )
            self.broker.create_order(order)

    def on_in_position(self, position: Position):
        if position.side is Side.LONG and self.candles.latest_close_price > 55_000:
            self.broker.close_position_market(position.symbol)
        elif position.side is Side.SHORT and self.candles.latest_close_price < 40_000:
            self.broker.close_position_market(position.symbol)


if __name__ == '__main__':

    start_cash = 1000
    base_currency = 'BTC'
    quote_currency = 'USDT'
    symbol = 'BTCUSDT'

    candles = get_store_candles(
        symbol=symbol,
        interval=Interval.HOUR_1,
        market=Market.FUTURES,
    ).between(
        start=datetime(year=2021, month=1, day=1),
        end=datetime(year=2022, month=1, day=2)
    )

    broker = BacktestFuturesBroker(
        balances=[Balance(time=candles.times[0], asset=quote_currency, available=start_cash)],
        symbols_set_leverage={symbol: 1},
        maker_fee_rate=0.0002,
        taker_fee_rate=0.0004,
    )

    strategy = StaticPriceStrategy(candles=candles, broker=broker)
    strategy.run()
    strategy.plot()
