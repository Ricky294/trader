import importlib
from typing import List

import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import BacktestFuturesTrader, BacktestPosition

from .log import logger
from .plot import Plot

from trader.core.const.candle_index import (
    OPEN_TIME_INDEX,
    OPEN_PRICE_INDEX,
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX,
    VOLUME_INDEX,
)
from trader.core.const.trade_actions import BUY
from trader.core.enum import CandlestickType
from trader.core.util.np import assign_where_not_zero

from trader.core.util.np import map_match
from trader.core.util.trade import to_heikin_ashi


def plot_backtest_results(
        candles: np.ndarray,
        trader: BacktestFuturesTrader,
        start_cash: float,
        log_scale=False,
        extra_plots: List[Plot] = None,
        candlestick_type: CandlestickType = CandlestickType.LINE,
):
    logger.info("Plotting results.")

    positions: List[BacktestPosition] = trader.positions

    def __create_custom_data(*arrays: np.ndarray):
        return np.stack(tuple(arrays), axis=-1)

    candle_open_times = candles[OPEN_TIME_INDEX]

    entry_time = map_match(candle_open_times, tuple(pos.times[0] for pos in positions))
    entry_price = assign_where_not_zero(entry_time, tuple(pos.prices[0] for pos in positions))
    quantity = assign_where_not_zero(entry_time, tuple(pos.quantities[0] for pos in positions))
    side = assign_where_not_zero(entry_time, tuple(pos.side for pos in positions))
    side = np.where(side == BUY, "Long", "Short")

    middle_time = map_match(candle_open_times, tuple(time for pos in positions for time in pos.times[1:-1]))
    middle_quantity = assign_where_not_zero(middle_time, tuple(quantity for pos in positions for quantity in pos.quantities[1:-1]))
    middle_price = assign_where_not_zero(middle_time, tuple(price for pos in positions for price in pos.prices[1:-1]))

    profit_array = np.array(tuple(pos.profit() for pos in positions))
    exit_time = map_match(candle_open_times, tuple(pos.times[-1] for pos in positions))
    exit_price = assign_where_not_zero(exit_time, tuple(pos.prices[-1] for pos in positions))
    exit_quantity = assign_where_not_zero(exit_time, tuple(pos.quantities[-1] for pos in positions))
    profit = assign_where_not_zero(exit_time, tuple(pos.profit() for pos in positions))

    capital = np.cumsum(profit) + start_cash

    entry_time[entry_time == 0.0] = np.nan
    middle_time[middle_time == 0.0] = np.nan
    exit_time[exit_time == 0.0] = np.nan

    is_candlestick = candlestick_type == CandlestickType.HEIKIN_ASHI or candlestick_type == CandlestickType.JAPANESE

    def create_plots():
        nonlocal entry_time
        nonlocal middle_time
        nonlocal exit_time

        high_price = candles[HIGH_PRICE_INDEX]
        low_price = candles[LOW_PRICE_INDEX]
        open_time = candles[OPEN_TIME_INDEX]
        close_price = candles[CLOSE_PRICE_INDEX]
        volume = candles[VOLUME_INDEX]

        if is_candlestick and (high_price is None or low_price is None):
            raise ValueError("high_price and low_price parameter is required if candlestick_plot is True")

        open_time = pd.to_datetime(open_time, unit="s")
        entry_time = pd.to_datetime(entry_time, unit="s")
        middle_time = pd.to_datetime(middle_time, unit="s")
        exit_time = pd.to_datetime(exit_time, unit="s")

        max_row = 2

        extra_graph_max_row = 0

        if extra_plots is not None:
            extra_graph_max_row = max((graph.number for graph in extra_plots))

        if extra_graph_max_row > 2:
            max_row = extra_graph_max_row

        row_heights = [1 for _ in range(max_row)]
        row_heights[1] = 2

        specs = [
            [{"type": "scatter"}],
            [{"secondary_y": True}],
        ]

        if extra_plots is not None:
            specs.extend([[{"type": graph.type.lower()}] for graph in extra_plots if graph.number > 2])

        fig = make_subplots(
            rows=max_row, cols=1,
            column_widths=[1.0],
            row_heights=row_heights,
            shared_xaxes=True,
            horizontal_spacing=0.0,
            vertical_spacing=0.02,
            specs=specs,
        )

        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=capital,
                name="Capital",
            ),
            row=1, col=1,
        )

        open_price = candles[OPEN_PRICE_INDEX]
        if candlestick_type == CandlestickType.HEIKIN_ASHI:
            open_price, high_price, low_price, close_price = to_heikin_ashi(
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
            )

        if is_candlestick:
            fig.add_trace(
                go.Candlestick(
                    x=open_time,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    name="Candles"
                ),
                secondary_y=False,
                row=2, col=1,
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=open_time,
                    y=close_price,
                    marker={"color": "#444"},
                    name="Close prices",
                ),
                row=2, col=1,
                secondary_y=False,
            )

        low_or_close_price = low_price if is_candlestick else close_price
        fig.add_trace(
            go.Scatter(
                x=entry_time,
                y=low_or_close_price - np.sqrt(low_or_close_price) * 2.,
                name="Entry",
                mode="markers",
                marker={"color": "#3d8f6d", "symbol": "triangle-up"},
                customdata=__create_custom_data(entry_price, side, quantity),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Side: %{customdata[1]}",
                    "Quantity: %{customdata[2]:.3f}",
                )),
            ),
            secondary_y=False,
            row=2, col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=middle_time,
                y=low_or_close_price - np.sqrt(low_or_close_price) * 2.,
                name="Adjust",
                mode="markers",
                marker={"color": "#ff9000", "symbol": "triangle-up"},
                customdata=__create_custom_data(middle_price, middle_quantity),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Quantity: %{customdata[1]:.3f}",
                )),
            ),
            secondary_y=False,
            row=2, col=1,
        )

        high_or_close_price = high_price if is_candlestick else close_price
        fig.add_trace(
            go.Scatter(
                x=exit_time,
                y=high_or_close_price + np.sqrt(high_or_close_price) * 2.,
                name="Exit",
                mode="markers",
                marker=dict(
                    color="red",
                    symbol="triangle-down",
                ),
                customdata=__create_custom_data(exit_price, exit_quantity, profit),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Quantity: %{customdata[1]:.3f}",
                    "Profit: %{customdata[2]:.2f}",
                ))
            ),
            secondary_y=False,
            row=2, col=1,
        )
        fig.update_xaxes(rangeslider={'visible': False}, row=2, col=1)

        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=volume,
                name="Volume",
                marker={"color": "#2CA02C"},
                opacity=0.2,
                hoverinfo='skip',
            ),
            secondary_y=True,
            row=2, col=1,
        )

        if extra_plots is not None:
            for graph in extra_plots:
                graph_module = importlib.import_module(f'plotly.graph_objects')
                graph_class = getattr(graph_module, graph.type.capitalize())
                graph_data = graph.data_callback(candles.T)
                for params in graph.params:
                    if "constant_y" in params:
                        y_data = [params.pop("constant_y")] * open_time.size
                    else:
                        y_data = graph_data[params.pop("y")]

                    fig.add_trace(
                        graph_class(
                            x=open_time,
                            y=y_data,
                            **params,
                        ),
                        row=graph.number, col=1,
                    )

        fig.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
        )
        if log_scale:
            fig.layout.yaxis1.type = "log"
            fig.layout.yaxis2.type = "log"

        fig.update_yaxes(tickformat=',.2f', visible=False, showticklabels=False, secondary_y=True)
        fig.layout.yaxis2.showgrid = False

        return fig

    def include_info_on_figure():
        wins = (profit_array > 0).sum()
        losses = (profit_array < 0).sum()
        win_rate = wins / (wins + losses)
        profit_sum = profit_array.sum()
        total_profit = (profit_sum + start_cash) / start_cash

        fig.add_annotation(
            text="<br>".join([
                f"Wins: {wins}, Losses: {losses}, Win rate: {(win_rate * 100):.3f}%",
                f"Largest win: {profit_array.max():.2f}, Largest loss: {profit_array.min():.2f}",
            ]),
            align="left",
            xref="x domain", yref="y domain",
            font=dict(
                size=8,
            ),
            x=0.005, y=0.99, showarrow=False,
            row=2, col=1,
        )

        fig.add_annotation(
            text="<br>".join([
                f"Final balance: {profit_sum + start_cash:.3f} ({'+' if profit_sum > 0 else ''}{total_profit * 100:.3f}%)",
                f"Total paid fee: {trader.total_paid_fee:.3f}"
            ]),
            align="left",
            xref="x domain", yref="y domain",
            font=dict(
                size=8,
            ),
            x=0.005, y=0.99, showarrow=False,
            row=1, col=1,
        )

    fig = create_plots()

    if len(positions) > 0:
        include_info_on_figure()

    fig.show()
