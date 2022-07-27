from trader.core.super_enum import OrderSide
from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesBroker
from trader.core.model import Balance
from trader.core.indicator import RSIIndicator
from trader.core.strategy.indicator import IndicatorStrategy
from trader.data.model import Candles
from trader.data.super_enum import Market

from trader.ui.enumerate import Candlestick, Volume


def take_profit_price_logic(candles: Candles, side: OrderSide):
    if side == OrderSide.BUY:
        return candles.latest_close_price * 1.1
    elif side == OrderSide.SELL:
        return candles.latest_close_price * 0.9


def stop_loss_price_logic(candles: Candles, side: OrderSide):
    if side == OrderSide.BUY:
        return candles.latest_close_price * 0.9
    elif side == OrderSide.SELL:
        return candles.latest_close_price * 1.1


if __name__ == "__main__":

    start_cash = 1000
    base_currency = "BTC"
    quote_currency = "USDT"

    rsi = RSIIndicator()

    candles = get_store_candles(
        base_currency=base_currency,
        quote_currency=quote_currency,
        interval="4h",
        market=Market.FUTURES,
        storage_type=HDF5CandleStorage,
    )

    strategy = IndicatorStrategy(
        broker=BacktestFuturesBroker(
            balance=Balance(asset=base_currency, available=start_cash),
            maker_fee_rate=0.0002,
            taker_fee_rate=0.0004,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=0.5,
        asset=base_currency,
        indicators=[rsi],
        entry_long_conditions=[rsi.oversold_reversal],
        entry_short_conditions=[rsi.overbought_reversal],
        profit_price=take_profit_price_logic,
        stop_price=stop_loss_price_logic,
    )

    strategy.run()
    strategy.plot(
        candlestick_type=Candlestick.JAPANESE,
        volume_type=Volume.LINE,
        custom_graphs=[rsi],
    )
