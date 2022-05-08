from __future__ import annotations

from typing import Iterable, Callable

from trader.data.binance import get_store_candles
from trader.data.database import HDF5CandleStorage
from trader.data.enum import Market

from trader.backtest import BacktestFuturesTrader
from trader.backtest.model import BacktestBalance
from trader.core.enumerate import OrderSide, Broker
from trader.core.indicator import Indicator
from trader.data.model import Candles

from trader.ui import CustomGraph
from trader.ui.enumerate import Candlestick, Volume


def run_backtest(
        broker: str | Broker,
        symbol: str,
        interval: str,
        market: str | Market,
        leverage: int,
        indicators: Iterable[Indicator],
        entry_long_conditions: Iterable[Callable[[], Iterable]],
        entry_short_conditions: Iterable[Callable[[], Iterable]],
        exit_long_conditions: Iterable[Callable[[], Iterable]] = (),
        exit_short_conditions: Iterable[Callable[[], Iterable]] = (),
        entry_price_logic: Callable[[Candles, OrderSide], float] = lambda _, __: None,
        exit_price_logic: Callable[[Candles, OrderSide], float] = lambda _, __: None,
        take_profit_price_logic: Callable[[Candles, OrderSide], float] = lambda _, __: None,
        stop_loss_price_logic: Callable[[Candles, OrderSide], float] = lambda _, __: None,
        trade_ratio=0.95,
        asset="USD",
        capital=1000,
        maker_fee_rate=0.0,
        taker_fee_rate=0.0,
        candlestick_type=Candlestick.LINE,
        volume_type=Volume.LINE,
        custom_graphs: Iterable[CustomGraph | Indicator] = (),
):
    from trader.core.strategy import AutoIndicatorStrategy

    if str(broker) == "BINANCE":
        candles = get_store_candles(
            symbol=symbol,
            interval=interval,
            market=market,
            storage_type=HDF5CandleStorage,
        )
    else:
        raise ValueError(f"Unsupported broker: {broker}")

    strategy = AutoIndicatorStrategy(
        symbol=symbol,
        asset=asset,
        candles=candles,
        indicators=indicators,
        leverage=leverage,
        trade_ratio=trade_ratio,
        trader=BacktestFuturesTrader(
            balance=BacktestBalance(asset=asset, free=capital),
            maker_fee_rate=maker_fee_rate,
            taker_fee_rate=taker_fee_rate
        ),
        entry_long_conditions=entry_long_conditions,
        entry_short_conditions=entry_short_conditions,
        exit_long_conditions=exit_long_conditions,
        exit_short_conditions=exit_short_conditions,
        entry_price_logic=entry_price_logic,
        exit_price_logic=exit_price_logic,
        take_profit_price_logic=take_profit_price_logic,
        stop_loss_price_logic=stop_loss_price_logic,
    )

    strategy.run()
    strategy.plot_results(
        candlestick_type=candlestick_type,
        volume_type=volume_type,
        custom_graphs=custom_graphs,
    )
