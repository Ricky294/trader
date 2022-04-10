from trader_data.binance import get_store_binance_candles
from trader_data.core.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesTrader, BacktestBalance
from trader.core.enum import Candlestick, OrderSide, Volume
from trader.core.indicator import RSIIndicator
from trader.core.strategy.auto import AutoStrategy


def take_profit_price_logic(side: OrderSide, current_price: float):
    if side == OrderSide.BUY:
        return current_price * 1.1
    elif side == OrderSide.SELL:
        return current_price * 0.9


def stop_loss_price_logic(side: OrderSide, current_price: float):
    if side == OrderSide.SELL:
        return current_price * 1.1
    elif side == OrderSide.BUY:
        return current_price * 0.9


if __name__ == "__main__":

    start_cash = 1000
    asset = "USD"
    symbol = "BTCUSDT"

    rsi = RSIIndicator()

    candles = get_store_binance_candles(
        symbol=symbol,
        interval="4h",
        market="FUTURES",
        storage_type=HDF5CandleStorage,
    )

    strategy = AutoStrategy(
        symbol=symbol,
        trader=BacktestFuturesTrader(
            balance=BacktestBalance(asset=asset, amount=start_cash),
            maker_fee_rate=0.0002,
            taker_fee_rate=0.0004,
        ),
        candles=candles,
        leverage=1,
        trade_ratio=0.5,
        asset=asset,
        indicators=[rsi],
        entry_long_conditions=[rsi.oversold],
        entry_short_conditions=[rsi.overbought],
        take_profit_price_logic=take_profit_price_logic,
        stop_loss_price_logic=stop_loss_price_logic,
    )

    strategy.run()
    strategy.plot_backtest(
        candlestick_type=Candlestick.HEIKIN_ASHI,
        volume_type=Volume.LINE,
        custom_graphs=[rsi],
    )
