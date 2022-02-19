import logging

from typing import List, Union, Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trader import PROFIT_PRECISION, MONEY_PRECISION, FEE_PRECISION, PRICE_PRECISION, QUANTITY_PRECISION
from trader.core.model.candles import Candles
from trader.core.const.trade_actions import BUY
from trader.core.enum import CandlestickType
from trader.core.util.np import assign_where_not_zero, map_match
from trader.core.util.trade import to_heikin_ashi

from .custom_graph import CustomGraph
from .position import BacktestPosition


class TradeResultFigure:

    @staticmethod
    def __create_custom_data(*arrays: np.ndarray):
        return np.stack(tuple(arrays), axis=-1)

    @staticmethod
    def __create_hover_template(names: List[str], precisions: List[Union[int, None]]):
        yield "%{x}"
        for i, (name, precision) in enumerate(zip(names, precisions)):
            if precision is None:
                yield f"{name}: %{{customdata[{i}]}}"
            else:
                yield f"{name}: %{{customdata[{i}]:.{precision}f}}"

    def __init__(
            self,
            candles: Candles,
            start_cash: float,
            positions: Iterable[BacktestPosition],
    ):
        self.graph_objects: List[dict] = []
        self.open_time = candles.open_times()
        self.open_price = candles.open_prices()
        self.high_price = candles.high_prices()
        self.low_price = candles.low_prices()
        self.close_price = candles.close_prices()
        self.volume = candles.volumes()

        self.entry_time = map_match(candles.open_times(), tuple(pos.entry_time for pos in positions))
        self.entry_price = assign_where_not_zero(self.entry_time, tuple(pos.entry_price for pos in positions))
        self.entry_fee = assign_where_not_zero(self.entry_time, tuple(pos.entry_fee for pos in positions))
        self.money = assign_where_not_zero(self.entry_time, tuple(pos.money() for pos in positions))
        self.quantity = assign_where_not_zero(self.entry_time, tuple(pos.quantity() for pos in positions))
        self.side = assign_where_not_zero(self.entry_time, tuple(pos.side for pos in positions))
        self.side = np.where(self.side == BUY, "Long", "Short")

        self.exit_time = map_match(candles.open_times(), tuple(pos.exit_time for pos in positions))
        self.exit_price = assign_where_not_zero(self.exit_time, tuple(pos.exit_price for pos in positions))
        self.exit_fee = assign_where_not_zero(self.exit_time, tuple(pos.exit_fee for pos in positions))
        self.profit = assign_where_not_zero(self.exit_time, tuple(pos.profit() for pos in positions))

        self.negative_profit = np.copy(self.profit)
        self.positive_profit = np.copy(self.profit)
        self.negative_profit[self.negative_profit > 0.0] = 0
        self.positive_profit[self.positive_profit < 0.0] = 0

        self.negative_profit_time = np.copy(self.exit_time)
        self.positive_profit_time = np.copy(self.exit_time)
        self.negative_profit_time[self.positive_profit != 0.0] = 0
        self.positive_profit_time[self.negative_profit != 0.0] = 0

        self.fee = np.cumsum(self.entry_fee + self.exit_fee)
        self.capital = np.cumsum(self.profit) + start_cash - self.fee

        self.entry_time[self.entry_time == 0.0] = np.nan
        self.exit_time[self.exit_time == 0.0] = np.nan
        self.negative_profit_time[self.negative_profit_time == 0.0] = np.nan
        self.positive_profit_time[self.positive_profit_time == 0.0] = np.nan

        self.open_time = pd.to_datetime(self.open_time, unit="s")
        self.entry_time = pd.to_datetime(self.entry_time, unit="s")
        self.exit_time = pd.to_datetime(self.exit_time, unit="s")
        self.negative_profit_time = pd.to_datetime(self.negative_profit_time, unit="s")
        self.positive_profit_time = pd.to_datetime(self.positive_profit_time, unit="s")

        self.capital_graph_number = None
        self.capital_graph = False

        self.profit_graph_number = None
        self.profit_graph = False

        self.candlestick_graph_number = None
        self.candlestick_graph = False

        self.profit_graph = False

        self.__graph_counter = 0

    def add_capital_graph(
            self,
            fee=True,
    ):
        self.__graph_counter += 1
        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.open_time,
                    y=self.capital,
                    name="Capital",
                    marker={"color": "#187bcd"},
                ),
                row=self.__graph_counter, col=1,
                secondary_y=False,
            )
        )
        if fee:
            self.graph_objects.append(
                dict(
                    trace=go.Scatter(
                        x=self.open_time,
                        y=self.fee,
                        opacity=0.25,
                        name="Fee",
                        marker={"color": "#444"},
                    ),
                    row=self.__graph_counter, col=1,
                    secondary_y=True,
                )
            )

        self.capital_graph = True
        self.capital_graph_number = self.__graph_counter

    def add_profit_graph(self):
        def log(data):
            data[data == 0.0] = np.nan
            log_data = np.log(np.absolute(data)) * 3
            return np.nan_to_num(log_data, copy=True, nan=0.0, posinf=None, neginf=None)

        self.__graph_counter += 1

        positive_profit_marker_size = np.absolute(log(self.positive_profit))
        negative_profit_marker_size = np.absolute(log(self.negative_profit))

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.negative_profit_time,
                    y=self.negative_profit,
                    name="Loss",
                    mode="markers",
                    marker=dict(
                        size=negative_profit_marker_size,
                        color="#B22222"
                    )
                ),
                row=self.__graph_counter, col=1,
                secondary_y=False,
            )
        )
        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.positive_profit_time,
                    y=self.positive_profit,
                    name="Profit",
                    mode="markers",
                    marker=dict(
                        size=positive_profit_marker_size,
                        color="#5CAA42"
                    )
                ),
                row=self.__graph_counter, col=1,
                secondary_y=False,
            )
        )

        self.profit_graph = True
        self.profit_graph_number = self.__graph_counter

    def add_candlestick_graph(
            self,
            type=CandlestickType.LINE,
    ):
        self.__graph_counter += 1

        is_candlestick = type == CandlestickType.HEIKIN_ASHI or type == CandlestickType.JAPANESE
        if is_candlestick and (self.high_price is None or self.low_price is None):
            raise ValueError("high_price and low_price parameter is required if candlestick_plot is True")

        if type == CandlestickType.HEIKIN_ASHI:
            self.open_price, self.high_price, self.low_price, self.close_price = to_heikin_ashi(
                open=self.open_price,
                high=self.high_price,
                low=self.low_price,
                close=self.close_price,
            )

        if is_candlestick:
            self.graph_objects.append(
                dict(
                    trace=go.Candlestick(
                        x=self.open_time,
                        open=self.open_price,
                        high=self.high_price,
                        low=self.low_price,
                        close=self.close_price,
                        name="Candles",
                    ),
                    secondary_y=False,
                    row=self.__graph_counter, col=1,
                )
            )

        else:
            self.graph_objects.append(
                dict(
                    trace=go.Scatter(
                        x=self.open_time,
                        y=self.close_price,
                        marker={"color": "#444"},
                        name="Close prices",
                    ),
                    row=self.__graph_counter, col=1,
                    secondary_y=False,
                )
            )

        low_or_close_price = self.low_price if is_candlestick else self.close_price
        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.entry_time,
                    y=low_or_close_price - np.sqrt(low_or_close_price) * 2.,
                    name="Entry",
                    mode="markers",
                    marker={"color": "#3d8f6d", "symbol": "triangle-up"},
                    customdata=self.__create_custom_data(self.entry_price, self.side, self.money, self.quantity, self.entry_fee),
                    hovertemplate="<br>".join(
                        self.__create_hover_template(
                            ["Price", "Side", "Money", "Quantity", "Fee"],
                            [PRICE_PRECISION, None, MONEY_PRECISION, QUANTITY_PRECISION, FEE_PRECISION],
                        )
                    ),
                ),
                secondary_y=False,
                row=self.__graph_counter, col=1,
            )
        )

        high_or_close_price = self.high_price if is_candlestick else self.close_price
        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.exit_time,
                    y=high_or_close_price + np.sqrt(high_or_close_price) * 2.,
                    name="Exit",
                    mode="markers",
                    marker=dict(
                        color="red",
                        symbol="triangle-down",
                    ),
                    customdata=self.__create_custom_data(self.exit_price, self.profit, self.exit_fee),
                    hovertemplate="<br>".join(
                        self.__create_hover_template(
                            ["Price", "Profit", "Fee"],
                            [PROFIT_PRECISION, PROFIT_PRECISION, FEE_PRECISION]
                        )
                    )

                ),
                secondary_y=False,
                row=self.__graph_counter, col=1,
            )
        )

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.open_time,
                    y=self.volume,
                    name="Volume",
                    marker={"color": "#2CA02C"},
                    opacity=0.2,
                    hoverinfo='skip',
                ),
                secondary_y=True,
                row=self.__graph_counter, col=1,
            )
        )

        self.candlestick_graph = True
        self.candlestick_graph_number = self.__graph_counter

    def add_custom_graphs(
            self,
            graphs: Iterable[CustomGraph],
    ):
        for graph in graphs:
            graph_class = getattr(go, graph.plot_type.capitalize())

            self.graph_objects.append(
                dict(
                    trace=graph_class(
                        x=self.open_time,
                        y=graph.y_data,
                        **graph.plot_params,
                    ),
                    row=graph.figure_index, col=1,
                )
            )

    def show(self):
        from . import BACKTEST_LOGGER
        logging.getLogger(BACKTEST_LOGGER).info("Plotting results.")

        number_of_plots = len(set(graph["row"] for graph in self.graph_objects))

        specs = [[{"secondary_y": True}] for _ in range(number_of_plots)]

        row_heights = []

        if self.capital_graph:
            row_heights.append(1.0)
        if self.profit_graph:
            row_heights.append(0.7)
        if self.candlestick_graph:
            row_heights.append(2.0)

        row_heights.extend([1 for _ in range(number_of_plots - len(row_heights))])

        if self.candlestick_graph:
            row_heights[self.candlestick_graph_number - 1] = 2.0

        fig = make_subplots(
            rows=number_of_plots, cols=1,
            column_widths=[1.0],
            row_heights=row_heights,
            shared_xaxes=True,
            horizontal_spacing=0.0,
            vertical_spacing=0.02,
            specs=specs,
        )

        for graph_object in self.graph_objects:
            fig.add_trace(**graph_object)

        fig.update_xaxes(rangeslider={'visible': False}, row=self.candlestick_graph_number, col=1)
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
        fig.update_yaxes(tickformat=',.2f', visible=False, showticklabels=False, secondary_y=True)
        fig.show()
