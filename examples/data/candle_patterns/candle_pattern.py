from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from trader.data.binance import get_store_candles
from trader.data.core import HDF5CandleStorage
from trader.data.enum import Market


class CandlestickPatternPlot:

    def __init__(self, symbol: str, interval: str, market: str | Market):
        self.symbol = symbol
        self.interval = interval
        self.market = market
        self.__get_candle_data()
        self.__add_candlestick_chart()

    def __get_candle_data(self):
        self.candles = get_store_candles(
            symbol=self.symbol,
            interval=self.interval,
            market=self.market,
            storage_type=HDF5CandleStorage,
        )

    def __add_candlestick_chart(self):
        self.fig = go.Figure()

        self.fig.add_trace(
            go.Candlestick(
                x=self.candles.pd_open_times(),
                open=self.candles.open_prices,
                high=self.candles.high_prices,
                low=self.candles.low_prices,
                close=self.candles.close_prices,
            )
        )

    def add_patterns(self, *names: str):
        for name in names:
            self.add_pattern(name)

    def add_pattern(self, name: str, *args, **kwargs):
        def add_text_plot(y, is_bullish, indexes):
            if is_bullish:
                pre_name = "Bullish"
                color = "green"
            else:
                pre_name = "Bearish"
                color = "red"

            self.fig.add_trace(
                go.Scatter(
                    x=self.candles.pd_open_times()[indexes],
                    y=y[indexes],
                    mode="text",
                    name=f"{pre_name} {name}",
                    text=name,
                    textfont=dict(
                        size=10,
                        color=color
                    )
                )
            )

        func_name = name.lower().replace(" ", "_")
        data = getattr(self.candles.patterns, func_name)(*args, **kwargs)

        name = name.capitalize().replace("_", " ")

        bullish_indexes, = np.where(data > 0)
        bearish_indexes, = np.where(data < 0)

        if len(bullish_indexes) > 0:
            y = self.candles.high_prices * 1.025
            add_text_plot(y, True, bullish_indexes)

        if len(bearish_indexes) > 0:
            y = self.candles.low_prices * 0.975
            add_text_plot(y, False, bearish_indexes)

    def show(self):
        self.fig.update_xaxes(rangeslider=dict(visible=False))
        self.fig.update_layout(dragmode='pan')
        self.fig.show(config=dict(scrollZoom=True))


plotter = CandlestickPatternPlot(
    symbol="BTCUSDT",
    interval="4h",
    market="SPOT",
)

plotter.add_patterns("three line strike", "three_black_crows", "evening_star", "abandoned_baby", "engulfing")
plotter.show()
