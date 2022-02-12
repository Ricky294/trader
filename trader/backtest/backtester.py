from tqdm import tqdm

from trader.core.strategy import Strategy

import importlib
from typing import List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .futures_trader import BacktestFuturesTrader
from trader.core.model.candles import Candles
from trader.core.log import logger
from .plot import Plot

from trader.core.const.trade_actions import BUY
from trader.core.enum import CandlestickType
from trader.core.util.np import assign_where_not_zero

from trader.core.util.np import map_match
from trader.core.util.trade import to_heikin_ashi


def __plot_backtest_results(
        candles: Candles,
        start_cash: float,
        trader: BacktestFuturesTrader,
        log_scale=False,
        extra_plots: List[Plot] = None,
        candlestick_type: CandlestickType = CandlestickType.LINE,
):
    def __create_custom_data(*arrays: np.ndarray):
        return np.stack(tuple(arrays), axis=-1)

    logger.info("Plotting results.")

    positions = trader.positions
    entry_time = map_match(candles.open_times(), tuple(pos.entry_time for pos in positions))
    entry_price = assign_where_not_zero(entry_time, tuple(pos.entry_price for pos in positions))
    entry_fee = assign_where_not_zero(entry_time, tuple(pos.entry_fee for pos in positions))
    money = assign_where_not_zero(entry_time, tuple(pos.money() for pos in positions))
    quantity = assign_where_not_zero(entry_time, tuple(pos.quantity() for pos in positions))
    side = assign_where_not_zero(entry_time, tuple(pos.side for pos in positions))
    side = np.where(side == BUY, "Long", "Short")

    profit_array = np.array(tuple(pos.profit() for pos in positions))
    exit_time = map_match(candles.open_times(), tuple(pos.exit_time for pos in positions))
    exit_price = assign_where_not_zero(exit_time, tuple(pos.exit_price for pos in positions))
    exit_fee = assign_where_not_zero(exit_time, tuple(pos.exit_fee for pos in positions))
    profit = assign_where_not_zero(exit_time, tuple(pos.profit() for pos in positions))

    fee = np.cumsum(entry_fee + exit_fee)

    capital = np.cumsum(profit) + start_cash - fee

    entry_time[entry_time == 0.0] = np.nan
    exit_time[exit_time == 0.0] = np.nan

    is_candlestick = candlestick_type == CandlestickType.HEIKIN_ASHI or candlestick_type == CandlestickType.JAPANESE

    def create_plots():
        nonlocal entry_time
        nonlocal exit_time

        open_time = candles.open_times()
        open_price = candles.open_prices()
        high_price = candles.high_prices()
        low_price = candles.low_prices()
        close_price = candles.close_prices()
        volume = candles.volumes()

        if is_candlestick and (high_price is None or low_price is None):
            raise ValueError("high_price and low_price parameter is required if candlestick_plot is True")

        open_time = pd.to_datetime(open_time, unit="s")
        entry_time = pd.to_datetime(entry_time, unit="s")
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
            [{"secondary_y": True}],
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
                y=fee,
                opacity=0.25,
                name="Fee",
                marker={"color": "#444"},
            ),
            row=1, col=1,
            secondary_y=True,
        )

        fig.add_trace(
            go.Scatter(
                x=open_time,
                y=capital,
                name="Capital",
                marker={"color": "#187bcd"},
            ),
            row=1, col=1,
            secondary_y=False,
        )

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
                customdata=__create_custom_data(entry_price, side, money, quantity, entry_fee),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Side: %{customdata[1]}",
                    "Money: %{customdata[2]:.2f}",
                    "Quantity: %{customdata[3]:.3f}",
                    "Fee: %{customdata[4]:.3f}",
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
                customdata=__create_custom_data(exit_price, profit, exit_fee),
                hovertemplate="<br>".join((
                    "%{x}",
                    "Price: %{customdata[0]:.2f}",
                    "Profit: %{customdata[1]:.2f}",
                    "Fee: %{customdata[2]:.3f}",
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
                graph_data = graph.data_callback(candles.array)
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

        fig.add_annotation(
            text="<br>".join([
                f"Wins: {wins}, Losses: {losses}, Win rate: {(win_rate * 100):.3f}%",
                f"Largest win: {profit_array.max():.2f}, Largest loss: {profit_array.min():.2f}",
            ]),
            align="left",
            xref="x domain", yref="y domain",
            font=dict(size=8),
            x=0.005, y=0.99, showarrow=False,
            row=2, col=1,
        )

        final_balance = trader.balance.free
        total_profit = (final_balance - start_cash) / start_cash
        fig.add_annotation(
            text="<br>".join([
                f"Final balance: {trader.balance.free:.3f} ({'+' if final_balance > start_cash else ''}{total_profit * 100:.3f}%)",
                f"Total paid fee: {np.sum(entry_fee + exit_fee):.3f}"
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


def run_backtest(
    candles: np.ndarray,
    strategy: Strategy,
    log_scale=False,
    candlestick_type=CandlestickType.LINE,
    extra_plots: List[Plot] = None,
):
    if not isinstance(strategy.trader, BacktestFuturesTrader):
        raise ValueError("Trader is not an instance of BacktestFuturesTrader!")

    candle_wrapper = Candles()
    logger.info(f"Running backtest on {len(candles)} candles.")
    for i in tqdm(range(1, len(candles))):
        candles_head = candles[:i]
        candle_wrapper.update(candles_head)
        strategy(candle_wrapper)
        strategy.trader(candle_wrapper)

    logger.info(
        f"Finished. Entered {len(strategy.trader.positions)} positions. "
        f"Final balance: {strategy.trader.balance.free:.3f}"
    )

    __plot_backtest_results(
        candles=candle_wrapper,
        trader=strategy.trader,
        start_cash=strategy.trader.start_balance.free,
        log_scale=log_scale,
        candlestick_type=candlestick_type,
        extra_plots=extra_plots,
    )
