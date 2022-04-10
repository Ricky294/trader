from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trader_data.core.model import Candles

from trader.config import PROFIT_PRECISION, MONEY_PRECISION, FEE_PRECISION, PRICE_PRECISION, QUANTITY_PRECISION
import trader.core.indicator as ind
import trader.core.util.format as fmt
import trader.core.util.vectorized.common as np_util
from trader.core.const.trade_actions import BUY
from trader.core.enum import Candlestick
from trader.core.enum.volume_type import Volume
from trader.core.log import get_core_logger
from trader.core.util.vectorized.trade import to_heikin_ashi
from trader.backtest.custom_graph import CustomGraph, Graph
from trader.backtest.position import BacktestPosition


class TradeResultFigure:

    @staticmethod
    def __create_custom_data(*arrays: np.ndarray):
        return np.stack(arrays, axis=-1)

    @staticmethod
    def __create_hover_template(names: Iterable[str], precisions: Iterable[int | None]):
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
            web_gl=True,
    ):
        self.web_gl = web_gl
        if web_gl:
            self.__scatter = go.Scattergl
        else:
            self.__scatter = go.Scatter

        self.candles = candles
        self.start_cash = start_cash

        self.graph_objects: list[dict] = []
        self.annotations: list[dict] = []

        self.open_time = candles.open_times
        self.open_price = candles.open_prices
        self.high_price = candles.high_prices
        self.low_price = candles.low_prices
        self.close_price = candles.close_prices
        self.volume = candles.volumes

        self.entry_time = np_util.replace_where_not_found(candles.open_times, np.array([pos.entry_time for pos in positions]), 0)
        entry_time_not_zero = self.entry_time != 0

        def replace_where_entry_time_is_not_zero(replacement):
            return np_util.replace_where(self.entry_time, entry_time_not_zero, replacement)

        self.entry_price = replace_where_entry_time_is_not_zero(tuple(pos.entry_price for pos in positions))
        self.entry_fee = replace_where_entry_time_is_not_zero(tuple(pos.entry_fee for pos in positions))
        self.money = replace_where_entry_time_is_not_zero(tuple(pos.money() for pos in positions))
        self.quantity = replace_where_entry_time_is_not_zero(tuple(pos.quantity() for pos in positions))
        self.side = replace_where_entry_time_is_not_zero(tuple(pos.side for pos in positions))
        self.side = np.where(self.side == BUY, "Long", "Short")

        self.exit_time = np_util.replace_where_not_found(candles.open_times, np.array([pos.exit_time for pos in positions]), 0)
        exit_time_not_zero = self.exit_time != 0

        def replace_where_exit_time_is_not_zero(replacement):
            return np_util.replace_where(self.exit_time, exit_time_not_zero, replacement)

        self.exit_price = replace_where_exit_time_is_not_zero(tuple(pos.exit_price for pos in positions))
        self.exit_fee = replace_where_exit_time_is_not_zero(tuple(pos.exit_fee for pos in positions))
        self.profit = replace_where_exit_time_is_not_zero(tuple(pos.profit() for pos in positions))

        self.negative_profit = self.profit.copy()
        self.positive_profit = self.profit.copy()
        self.negative_profit[self.negative_profit > 0.0] = 0
        self.positive_profit[self.positive_profit < 0.0] = 0

        self.negative_profit_time = self.exit_time.copy()
        self.positive_profit_time = self.exit_time.copy()
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

        self._graph_counter = 0

    def add_capital_graph(
            self,
            fee=True,
            fee_color="#444",
            capital_color="#187bcd",
            annotation=True,
    ):
        self._graph_counter += 1
        self.graph_objects.append(
            dict(
                trace=self.__scatter(
                    x=self.open_time,
                    y=self.capital,
                    name="Capital",
                    marker={"color": capital_color},
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )
        if fee:
            self.graph_objects.append(
                dict(
                    trace=self.__scatter(
                        x=self.open_time,
                        y=self.fee,
                        opacity=0.25,
                        name="Fee",
                        marker={"color": fee_color},
                    ),
                    row=self._graph_counter, col=1,
                    secondary_y=True,
                )
            )

        if annotation:
            final_balance = float(self.capital[-1])
            total_profit = (final_balance - self.start_cash) / self.start_cash
            self.annotations.append(
                dict(
                    text="<br>".join([
                        f"Final balance: {fmt.num(final_balance, MONEY_PRECISION)}"
                        f"({fmt.num(total_profit, perc=True, plus=True)})",
                        f"Total paid fee: {fmt.num(self.fee[-1], FEE_PRECISION)}",
                    ]),
                    align="left",
                    xref="x domain", yref="y domain",
                    font=dict(
                        size=8,
                    ),
                    x=0.005, y=0.99, showarrow=False,
                    row=self._graph_counter, col=1,
                )
            )

        self.capital_graph = True
        self.capital_graph_number = self._graph_counter

    def add_profit_graph(
            self,
            profit_marker_color="#5CAA42",
            loss_marker_color="#B22222",
            annotation=True,
    ):
        def apply_logarithm(data):
            data[data == 0.0] = np.nan
            log_data = np.log(np.absolute(data)) * 3
            nan_mask = np.isnan(log_data)
            log_data[nan_mask] = 0.0
            return log_data

        self._graph_counter += 1

        positive_profit_marker_size = np.absolute(apply_logarithm(self.positive_profit))
        negative_profit_marker_size = np.absolute(apply_logarithm(self.negative_profit))

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.positive_profit_time,
                    y=self.positive_profit,
                    name="Profit",
                    mode="markers",
                    marker=dict(
                        size=positive_profit_marker_size,
                        color=profit_marker_color,
                    )
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )
        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.negative_profit_time,
                    y=self.negative_profit,
                    name="Loss",
                    mode="markers",
                    marker=dict(
                        size=negative_profit_marker_size,
                        color=loss_marker_color,
                    )
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )

        if annotation:
            number_of_wins = (self.profit > 0).sum()
            number_of_losses = (self.profit < 0).sum()
            win_rate = number_of_wins / (number_of_wins + number_of_losses)

            losses = self.profit[self.profit < 0]
            wins = self.profit[self.profit > 0]

            avg_win_loss = (wins.sum() + losses.sum()) / len(self.profit[self.profit != 0])
            self.annotations.append(
                dict(
                    text="<br>".join([
                        f"Wins: {number_of_wins}, Losses: {number_of_losses}, "
                        f"Win rate: {fmt.num(win_rate, 3, perc=True)}%",
                        f"Largest win: {fmt.num(self.profit.max(), PROFIT_PRECISION, plus=True)} "
                        f"Largest loss: {fmt.num(self.profit.min(), PROFIT_PRECISION)}",
                        f"Average win/loss: {fmt.num(avg_win_loss, PROFIT_PRECISION, plus=True)}",
                    ]),
                    align="left",
                    xref="x domain", yref="y domain",
                    font=dict(size=8),
                    x=0.005, y=0.99, showarrow=False,
                    row=self._graph_counter, col=1,
                )
            )

        self.profit_graph = True
        self.profit_graph_number = self._graph_counter

    def add_candlestick_graph(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type=Volume.LINE,
            entry_marker_color="#3d8f6d",
            exit_marker_color="red",
            volume_color="#2CA02C",
            annotation=True,
    ):
        self._graph_counter += 1

        open_price = self.open_price
        high_price = self.high_price
        low_price = self.low_price
        close_price = self.close_price

        if candlestick_type == Candlestick.HEIKIN_ASHI:
            open_price, high_price, low_price, close_price = to_heikin_ashi(
                open=self.open_price,
                high=self.high_price,
                low=self.low_price,
                close=self.close_price,
            )

        is_candlestick = candlestick_type in (Candlestick.HEIKIN_ASHI, Candlestick.JAPANESE)
        if is_candlestick:
            self.graph_objects.append(
                dict(
                    trace=go.Candlestick(
                        x=self.open_time,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        name=f"Candles ({str(candlestick_type)})",
                    ),
                    secondary_y=False,
                    row=self._graph_counter, col=1,
                )
            )

        else:
            self.graph_objects.append(
                dict(
                    trace=self.__scatter(
                        x=self.open_time,
                        y=close_price,
                        marker=dict(color="#444"),
                        name="Close prices",
                    ),
                    row=self._graph_counter, col=1,
                    secondary_y=False,
                )
            )

        low_or_close_price = self.low_price if is_candlestick else self.close_price
        self.graph_objects.append(
            dict(
                trace=self.__scatter(
                    x=self.entry_time,
                    y=low_or_close_price - np.sqrt(low_or_close_price) * 2.,
                    name="Entry",
                    mode="markers",
                    marker={"color": entry_marker_color, "symbol": "triangle-up"},
                    customdata=self.__create_custom_data(
                        self.entry_price, self.side, self.money, self.quantity, self.entry_fee
                    ),
                    hovertemplate="<br>".join(
                        self.__create_hover_template(
                            ["Price", "Side", "Money", "Quantity", "Fee"],
                            [PRICE_PRECISION, None, MONEY_PRECISION, QUANTITY_PRECISION, FEE_PRECISION],
                        )
                    ),
                ),
                secondary_y=False,
                row=self._graph_counter, col=1,
            )
        )

        high_or_close_price = self.high_price if is_candlestick else self.close_price
        self.graph_objects.append(
            dict(
                trace=self.__scatter(
                    x=self.exit_time,
                    y=high_or_close_price + np.sqrt(high_or_close_price) * 2.,
                    name="Exit",
                    mode="markers",
                    marker=dict(
                        color=exit_marker_color,
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
                row=self._graph_counter, col=1,
            )
        )

        if volume_type == Volume.LINE:
            self.graph_objects.append(
                dict(
                    trace=self.__scatter(
                        x=self.open_time,
                        y=self.volume,
                        name="Volume (Line)",
                        marker={"color": volume_color},
                        opacity=0.2,
                        hoverinfo='skip',
                    ),
                    secondary_y=True,
                    row=self._graph_counter, col=1,
                )
            )
        elif volume_type == Volume.BAR:
            self.graph_objects.append(
                dict(
                    trace=go.Bar(
                        x=self.open_time,
                        y=self.volume,
                        name="Volume (Bar)",
                        marker={"color": volume_color},
                        opacity=0.2,
                        hoverinfo='skip',
                    ),
                    secondary_y=True,
                    row=self._graph_counter, col=1,
                )
            )

        if annotation:
            self.annotations.append(
                dict(
                    text="<br>".join([
                        f"ATH: {fmt.num(self.candles.ath(), PRICE_PRECISION)}",
                        f"ATL: {fmt.num(self.candles.atl(), PRICE_PRECISION)}",
                    ]),
                    align="left",
                    xref="x domain", yref="y domain",
                    font=dict(size=8),
                    x=0.005, y=0.99, showarrow=False,
                    row=self._graph_counter, col=1,

                )
            )

        self.candlestick_graph = True
        self.candlestick_graph_number = self._graph_counter

    def _get_graph_number(self, graph: Graph):
        if graph == Graph.CAPITAL:
            return self.capital_graph_number
        elif graph == Graph.MAIN:
            return self.candlestick_graph_number
        elif graph == Graph.PROFIT:
            return self.profit_graph_number
        elif graph == Graph.NEW:
            self._graph_counter += 1
            return self._graph_counter

    def add_custom_graph(
            self,
            graph: CustomGraph,
    ):
        if isinstance(graph.y, (float, int)):
            x = [self.open_time[0], self.open_time[-1]]
            y = [graph.y, graph.y]
        else:
            x = self.open_time
            y = graph.y

        self.graph_objects.append(
            dict(
                trace=graph.type(
                    x=x,
                    y=y,
                    **graph.params,
                ),
                row=self._get_graph_number(graph.selected), col=1,
            )
        )

    def add_indicator_graph(self, indicator: ind.Indicator):
        indicator(self.candles)

        main_graph_indicators = (
            ind.SingleMAIndicator,
            ind.DoubleMAIndicator,
            ind.MeanReversionIndicator,
            ind.BBANDSIndicator,
            ind.KeltnerChannelsIndicator,
        )

        indicator_name = indicator.__class__.__name__

        if indicator_name in (i.__name__ for i in main_graph_indicators):
            figure_number = self.candlestick_graph_number
        else:
            self._graph_counter += 1
            figure_number = self._graph_counter

        for name, y_data in indicator.__dict__.items():
            if isinstance(y_data, np.ndarray):
                self.graph_objects.append(
                    dict(
                        trace=self.__scatter(
                            x=self.open_time,
                            y=y_data,
                            name=fmt.upper(name),
                        ),
                        row=figure_number, col=1,
                    )
                )
            elif "limit" in name and isinstance(y_data, (float, int)):
                self.graph_objects.append(
                    dict(
                        trace=self.__scatter(
                            x=[self.open_time[0], self.open_time[-1]],
                            y=[y_data, y_data],
                            mode="lines",
                            hoverinfo='skip',
                            marker=dict(color="#187bcd"),
                            name=fmt.capitalize(name, y_data),
                        ),
                        row=figure_number, col=1,
                    )
                )

    def show(self):
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

        for annotation in self.annotations:
            fig.add_annotation(**annotation)

        fig.update_xaxes(rangeslider={'visible': False}, row=self.candlestick_graph_number, col=1)
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), legend={'itemsizing': 'constant'}, dragmode='pan')
        fig.update_yaxes(visible=True, showgrid=False, zeroline=False, showticklabels=True, secondary_y=True)

        get_core_logger().info("Plotting results.")

        config = dict({'scrollZoom': True})
        fig.show(config=config)
