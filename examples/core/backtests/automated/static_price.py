from datetime import datetime

from trader.backtest import BacktestFuturesBroker
from trader.core.model import Balance, Order, Position

from trader.core.super_enum import OrderSide
from trader.core.strategy import CallbackStrategy

from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage
from trader.data.model import Candles
from trader.data.super_enum import Market

from trader.ui.enumerate import Candlestick


def enter_position_callback(candles: Candles, balance: Balance, orders: list[Order]):
    if candles.latest_close_price > 40_000 > candles.close_prices[-2]:
        return OrderSide.LONG
    elif candles.latest_close_price > 60_000 > candles.close_prices[-2]:
        return OrderSide.SHORT


def exit_position_callback(candles: Candles, balance: Balance, orders: list[Order], position: Position):
    if position.side == OrderSide.LONG and candles.latest_close_price > 55_000:
        return True
    elif position.side == OrderSide.SHORT and candles.latest_close_price < 40_000:
        return True


if __name__ == "__main__":

    start_cash = 1000
    base_currency = "BTC"
    quote_currency = "USDT"

    candles = get_store_candles(
        base_currency=base_currency,
        quote_currency=quote_currency,
        interval="1d",
        market=Market.FUTURES,
        storage_type=HDF5CandleStorage,
    )
    candles = candles.between(start=datetime(year=2021, month=1, day=1), end=datetime(year=2022, month=1, day=2))

    strategy = CallbackStrategy(
        broker=BacktestFuturesBroker(
            balance=Balance(time=candles.times[0], asset=quote_currency, available=start_cash),
            maker_fee_rate=0.0002,
            taker_fee_rate=0.0004,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=1,
        asset=quote_currency,
        enter_position_callback=enter_position_callback,
        exit_position_callback=exit_position_callback,
    )

    strategy.run()
    strategy.plot(candlestick_type=Candlestick.JAPANESE,)
