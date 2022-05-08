from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage

from trader.backtest import BacktestFuturesTrader
from trader.backtest.model import BacktestBalance
from trader.core.enumerate import OrderSide
from trader.core.indicator import RSIIndicator
from trader.core.strategy.auto_indicator import AutoIndicatorStrategy

from trader.ui.enumerate import Candlestick, Volume


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

    candles = get_store_candles(
        symbol=symbol,
        interval="4h",
        market="FUTURES",
        storage_type=HDF5CandleStorage,
    )

    strategy = AutoIndicatorStrategy(
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
        entry_long_conditions=[rsi.oversold_reversal],
        entry_short_conditions=[rsi.overbought_reversal],
        take_profit_price_logic=take_profit_price_logic,
        stop_loss_price_logic=stop_loss_price_logic,
    )

    strategy.run()
    strategy.plot_results(
        candlestick_type=Candlestick.JAPANESE,
        volume_type=Volume.LINE,
        custom_graphs=[rsi],
    )
