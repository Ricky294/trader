from __future__ import annotations

from typing import Iterable

import numpy as np
import nputils as npu
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trader.data.model import Candles

from trader.config import PROFIT_PRECISION, MONEY_PRECISION, FEE_PRECISION, PRICE_PRECISION, QUANTITY_PRECISION
import trader.core.indicator as ind
import trader.core.util.format as fmt
from trader.core.model import Positions

from trader.ui import CustomGraph
from trader.ui.enumerate import Candlestick, Volume, Graph


class TradeGraphs:

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

    @staticmethod
    def _create_full_series(time_series, positions: Positions, start_cash: float):
        entry_time = npu.replace_where_not_found(time_series, positions.entry_time, 0)
        entry_fee = npu.replace_where(entry_time, entry_time != 0, positions.entry_fee)

        exit_time = npu.replace_where_not_found(time_series, positions.exit_time, 0)
        exit_fee = npu.replace_where(exit_time, exit_time != 0, positions.exit_fee)
        profit = npu.replace_where(exit_time, exit_time != 0, positions.profit)

        fee = np.cumsum(entry_fee + exit_fee)
        capital = np.cumsum(profit) + start_cash - fee

        return fee, capital

    def __init__(
            self,
            candles: Candles,
            positions: Positions,
            start_cash: float,
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

        self.capital_graph_number = None
        self.capital_graph = False

        self.profit_graph_number = None
        self.profit_graph = False

        self.candlestick_graph_number = None
        self.candlestick_graph = False

        self.profit_graph = False
        self._graph_counter = 0

        # --- Calculate series --- #
        self.positions = positions
        self.fee, self.capital = self._create_full_series(candles.open_times, positions, start_cash)

        # https://stackoverflow.com/questions/33678543/finding-indices-of-matches-of-one-array-in-another-array
        self.entry_indexes = np.nonzero(np.isin(self.candles.open_times, positions.entry_time))[0]
        self.exit_indexes = np.nonzero(np.isin(self.candles.open_times, positions.exit_time))[0]

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
                    x=self.candles.pd_open_times,
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
                        x=self.candles.pd_open_times,
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
                        f"Final balance: {fmt.num(final_balance, MONEY_PRECISION)} "
                        f"({fmt.num(total_profit, PROFIT_PRECISION, perc=True, plus=True)})",
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
            log_data = np.log(np.absolute(data)) * 3
            nan_mask = np.isnan(log_data)
            log_data[nan_mask] = 0.0
            return log_data

        self._graph_counter += 1

        positive_profit_marker_size = np.absolute(apply_logarithm(self.positions.positive_profit))
        negative_profit_marker_size = np.absolute(apply_logarithm(self.positions.negative_profit))

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.positions.pd_positive_profit_time,
                    y=self.positions.positive_profit,
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
                    x=self.positions.pd_negative_profit_time,
                    y=self.positions.negative_profit,
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
            wins = len(self.positions.positive_profit)
            losses = len(self.positions.negative_profit)
            win_rate = wins / (wins + losses)
            avg_win_loss = (np.sum(self.positions.positive_profit) + np.sum(self.positions.negative_profit)) / len(self.positions.profit)
            self.annotations.append(
                dict(
                    text="<br>".join([
                        f"Wins: {wins}, Losses: {losses}, "
                        f"Win rate: {fmt.num(win_rate, 3, perc=True)}",
                        f"Largest win: {fmt.num(np.max(self.positions.profit), PROFIT_PRECISION, plus=True)} "
                        f"Largest loss: {fmt.num(np.min(self.positions.profit), PROFIT_PRECISION)}",
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

        def append_candlestick_graph(candles: Candles):
            self.graph_objects.append(
                dict(
                    trace=go.Candlestick(
                        x=candles.pd_open_times,
                        open=candles.open_prices,
                        high=candles.high_prices,
                        low=candles.low_prices,
                        close=candles.close_prices,
                        name=f"Candles ({str(candlestick_type)})",
                    ),
                    secondary_y=False,
                    row=self._graph_counter, col=1,
                )
            )

        self._graph_counter += 1

        if candlestick_type is Candlestick.HEIKIN_ASHI:
            append_candlestick_graph(self.candles.to_heikin_ashi())
        elif candlestick_type is Candlestick.JAPANESE:
            append_candlestick_graph(self.candles)
        else:
            self.graph_objects.append(
                dict(
                    trace=self.__scatter(
                        x=self.candles.pd_open_times,
                        y=self.candles.close_prices,
                        marker=dict(color="#444"),
                        name="Close prices",
                    ),
                    row=self._graph_counter, col=1,
                    secondary_y=False,
                )
            )

        is_candlestick = candlestick_type in (Candlestick.HEIKIN_ASHI, Candlestick.JAPANESE)
        entry_y = self.candles.low_prices if is_candlestick else self.candles.close_prices
        entry_y = entry_y[self.entry_indexes]
        self.graph_objects.append(
            dict(
                trace=self.__scatter(
                    x=self.positions.pd_entry_time,
                    y=entry_y - np.sqrt(entry_y) * 2.,
                    name="Entry",
                    mode="markers",
                    marker={"color": entry_marker_color, "symbol": "triangle-up"},
                    customdata=self.__create_custom_data(
                        self.positions.entry_price, self.positions.side, self.positions.money, self.positions.quantity, self.positions.entry_fee
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

        exit_y = self.candles.high_prices if is_candlestick else self.candles.close_prices
        exit_y = exit_y[self.exit_indexes]
        self.graph_objects.append(
            dict(
                trace=self.__scatter(
                    x=self.positions.pd_exit_time,
                    y=exit_y + np.sqrt(exit_y) * 2.,
                    name="Exit",
                    mode="markers",
                    marker=dict(
                        color=exit_marker_color,
                        symbol="triangle-down",
                    ),
                    customdata=self.__create_custom_data(self.positions.exit_price, self.positions.profit, self.positions.exit_fee),
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
                        x=self.candles.pd_open_times,
                        y=self.candles.volumes,
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
                        x=self.candles.pd_open_times,
                        y=self.candles.volumes,
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

    def add_graphs(self, graphs: Iterable[CustomGraph | ind.Indicator]):
        for graph in graphs:
            if isinstance(graph, CustomGraph):
                self._add_custom_graph(graph)
            elif isinstance(graph, ind.Indicator):
                self._add_indicator_graph(graph)

    def _add_custom_graph(self, graph: CustomGraph):
        if isinstance(graph.y, (float, int)):
            x = [self.candles.pd_open_times[0], self.candles.pd_open_times[-1]]
            y = [graph.y, graph.y]
        else:
            x = self.candles.pd_open_times
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

    def _add_indicator_graph(self, indicator: ind.Indicator):
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
                            x=self.candles.pd_open_times,
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
                            x=[self.candles.pd_open_times[0], self.candles.pd_open_times[-1]],
                            y=[y_data, y_data],
                            mode="lines",
                            hoverinfo='skip',
                            marker=dict(color="#187bcd"),
                            name=fmt.capitalize(name, y_data),
                        ),
                        row=figure_number, col=1,
                    )
                )

    def create_figure(self):
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

        return fig
