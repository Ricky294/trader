from __future__ import annotations

from typing import Iterable

import numpy as np
import nputils as npu
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trader.core.model.balances import Balances
from trader.data.model import Candles

from trader.settings import Settings
from trader.core.model import Positions

from trader.ui import CustomGraph
from trader.ui.const import Candlestick, Volume, Graph

import util.format_util as fmt


class TradeGraphs:

    @staticmethod
    def _create_full_series(time_series, positions: Positions, start_cash: float):
        entry_time = npu.replace_where_not_found(time_series, positions.entry_timestamp, 0)
        close_time = npu.replace_where_not_found(time_series, positions.close_timestamp, 0)

        entry_fee = npu.replace_where(entry_time, entry_time != 0, positions.entry_fee)
        close_fee = npu.replace_where(close_time, close_time != 0, positions.close_fee)

        profit = npu.replace_where(close_time, close_time != 0, positions.close_profit)

        cum_fee = np.cumsum(entry_fee + close_fee)
        cum_capital = np.cumsum(profit) + start_cash - cum_fee

        return cum_fee, cum_capital

    def __init__(
            self,
            candles: Candles,
            positions: Positions,
            balances: Balances,
    ):
        self.candles = candles
        self.positions = positions
        self.balances = balances

        self.start_cash = balances[0].total

        self.cum_fee, self.cum_capital = self._create_full_series(candles.timestamps, positions, self.start_cash)

        self.final_balance = float(self.cum_capital[-1])
        self.total_profit = (self.final_balance - self.start_cash) / self.start_cash

        # https://stackoverflow.com/questions/33678543/finding-indices-of-matches-of-one-array-in-another-array
        self.entry_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.entry_timestamp))[0]
        self.long_entry_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.long_entry_timestamp))[0]
        self.short_entry_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.short_entry_timestamp))[0]

        self.adjust_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.adjust_timestamp))[0]
        self.long_adjust_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.long_adjust_timestamp))[0]
        self.short_adjust_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.short_adjust_timestamp))[0]

        self.close_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.close_timestamp))[0]
        self.long_close_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.long_close_timestamp))[0]
        self.short_close_indexes = np.nonzero(np.isin(self.candles.timestamps, positions.short_close_timestamp))[0]


class MatplotTradeGraphs(TradeGraphs):

    def __init__(self, candles: Candles, positions: Positions, balances: Balances):
        super().__init__(
            candles=candles,
            positions=positions,
            balances=balances
        )


class PlotlyTradeGraphs(TradeGraphs):

    OPTIMIZE_GRAPH_THRESHOLD = 2_500

    @staticmethod
    def _create_custom_data(*arrays: np.ndarray):
        return np.stack(arrays, axis=-1)

    @staticmethod
    def _create_hover_template(names: Iterable[str], precisions: Iterable[int | None]):
        yield '%{x}'
        for i, (name, precision) in enumerate(zip(names, precisions)):
            if precision is None:
                yield f'{name}: %{{customdata[{i}]}}'
            else:
                yield f'{name}: %{{customdata[{i}]:.{precision}f}}'

    def __init__(self, candles: Candles, positions: Positions, balances: Balances, web_gl=True):
        super().__init__(
            candles=candles,
            positions=positions,
            balances=balances
        )

        self.web_gl = web_gl
        if web_gl:
            self._scatter = go.Scattergl
        else:
            self._scatter = go.Scatter

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

    def add_capital_graph(
            self,
            fee=True,
            fee_color='#444',
            capital_color='#187bcd',
            annotation=True,
    ):
        self._graph_counter += 1
        self.graph_objects.append(
            dict(
                trace=self._scatter(
                    x=self.candles.times,
                    y=self.cum_capital,
                    name='Capital',
                    marker={'color': capital_color},
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )
        if fee:
            self.graph_objects.append(
                dict(
                    trace=self._scatter(
                        x=self.candles.times,
                        y=self.cum_fee,
                        opacity=0.25,
                        name='Fee',
                        marker={'color': fee_color},
                    ),
                    row=self._graph_counter, col=1,
                    secondary_y=True,
                )
            )

        if annotation:
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'Start balance: {fmt.num(self.start_cash, prec=Settings.precision_balance)} ',
                        f'Final balance: {fmt.num(self.final_balance, prec=Settings.precision_balance)} '
                        f'({fmt.num(self.total_profit, prec=Settings.precision_profit, perc=True, plus=True)})',
                        f'Total paid fee: {fmt.num(self.cum_fee[-1], prec=Settings.precision_fee)}',
                    ]),
                    align='left',
                    xref='x domain', yref='y domain',
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
            profit_marker_color='#5CAA42',
            loss_marker_color='#B22222',
            annotation=True,
    ):
        def apply_logarithm(data):
            log_data = np.log(np.absolute(data)) * 3
            nan_mask = np.isnan(log_data)
            log_data[nan_mask] = 0.0
            return log_data

        self._graph_counter += 1

        positive_profit_marker_size = np.absolute(apply_logarithm(self.positions.positive_close_profit))
        negative_profit_marker_size = np.absolute(apply_logarithm(self.positions.negative_close_profit))

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.positions.positive_close_profit_time,
                    y=self.positions.positive_close_profit,
                    name='Profit',
                    mode='markers',
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
                    x=self.positions.negative_close_profit_time,
                    y=self.positions.negative_close_profit,
                    name='Loss',
                    mode='markers',
                    marker=dict(
                        size=negative_profit_marker_size,
                        color=loss_marker_color,
                    )
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=self.positions.zero_close_profit_time,
                    y=self.positions.zero_close_profit,
                    name='0 Profit',
                    mode='markers',
                    marker=dict(
                        size=2,
                        color='#999999',
                    )
                ),
                row=self._graph_counter, col=1,
                secondary_y=False,
            )
        )

        if annotation:
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'Wins: {self.positions.number_of_wins}, Losses: {self.positions.number_of_losses}, '
                        f'Win rate: {fmt.num(self.positions.win_rate, prec=3, perc=True)}',
                        f'Largest win: {fmt.num(self.positions.largest_profit, prec=Settings.precision_profit, plus=True)} '
                        f'Largest loss: {fmt.num(self.positions.largest_loss, prec=Settings.precision_profit)}',
                        f'Average win/loss: {fmt.num(self.positions.average_profit_and_loss, prec=Settings.precision_profit, plus=True)}',
                    ]),
                    align='left',
                    xref='x domain', yref='y domain',
                    font=dict(size=8),
                    x=0.005, y=0.99, showarrow=False,
                    row=self._graph_counter, col=1,
                )
            )

        self.profit_graph = True
        self.profit_graph_number = self._graph_counter

    def __create_marker(
            self,
            x,
            y,
            name: str,
            color: str,
            symbol: str,
            hovertemplate: Iterable[str] = None,
            customdata: Iterable = None,
            text_position: str = None,
            text: Iterable[str] = None,
    ):
        return dict(
            trace=self._scatter(
                x=x,
                y=y,
                name=name,
                mode='markers+text',
                marker=dict(color=color, symbol=symbol),
                text=text,
                textposition=text_position,
                textfont=dict(
                    size=9,
                ),
                customdata=customdata,
                hovertemplate=None if hovertemplate is None else '<br>'.join(hovertemplate),
            ),
            secondary_y=False,
            row=self._graph_counter, col=1,
        )

    def add_candlestick_graph(
            self,
            candlestick_type=Candlestick.AUTO,
            side_labels=True,
            price_markers=True,
            long_entry_marker_color='#257450',
            long_adjust_marker_color='orange',
            long_exit_marker_color='#257450',
            short_entry_marker_color='red',
            short_adjust_marker_color='orange',
            short_close_marker_color='red',
            entry_price_marker_color='#2871cc',
            adjust_price_marker_color='#2871cc',
            close_price_marker_color='#2871cc',
            annotation=True,
    ):
        candle_len = len(self.candles)
        hover_text = np.array([f'count: {fmt.num(i + 1)}/{fmt.num(candle_len)}' for i in range(candle_len)])

        if candlestick_type is Candlestick.AUTO:
            if candle_len > self.OPTIMIZE_GRAPH_THRESHOLD:
                candlestick_type = Candlestick.LINE
            else:
                candlestick_type = Candlestick.JAPANESE

        def append_candlestick_graph(candles: Candles):
            self.graph_objects.append(
                dict(
                    trace=go.Candlestick(
                        x=candles.times,
                        open=candles.open_prices,
                        high=candles.high_prices,
                        low=candles.low_prices,
                        close=candles.close_prices,
                        name=f'Candles ({str(candlestick_type)})',
                        hovertext=hover_text,
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
                    trace=self._scatter(
                        x=self.candles.times,
                        y=self.candles.close_prices,
                        marker=dict(color='#444'),
                        name='Close prices',
                    ),
                    row=self._graph_counter, col=1,
                    secondary_y=False,
                )
            )

        is_candlestick = candlestick_type in [Candlestick.HEIKIN_ASHI, Candlestick.JAPANESE]

        entry_long_y = self.candles.low_prices if is_candlestick else self.candles.close_prices
        entry_long_y = entry_long_y[self.long_entry_indexes]
        self.graph_objects.append(
            self.__create_marker(
                name='Long entry',
                x=self.positions.long_entry_time,
                y=entry_long_y - np.sqrt(entry_long_y) * 2.,
                color=long_entry_marker_color,
                symbol='triangle-up',
                text=['Long'] * len(self.positions.long_entry_time) if side_labels else None,
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.long_entry_price,
                    self.positions.long_entry_amount,
                    self.positions.long_entry_quantity,
                    self.positions.long_entry_leverage,
                    self.positions.long_entry_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Leverage', 'Fee'],
                    [Settings.precision_price, Settings.precision_money,
                     Settings.precision_quantity, None, Settings.precision_fee],
                )
            )
        )

        entry_short_y = self.candles.low_prices if is_candlestick else self.candles.close_prices
        entry_short_y = entry_short_y[self.short_entry_indexes]
        self.graph_objects.append(
            self.__create_marker(
                x=self.positions.short_entry_time,
                y=entry_short_y - np.sqrt(entry_short_y) * 2.,
                name='Short entry',
                color=short_entry_marker_color,
                symbol='triangle-up',
                text=['Short'] * len(self.positions.short_entry_time) if side_labels else None,
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.short_entry_price,
                    self.positions.short_entry_amount,
                    self.positions.short_entry_quantity,
                    self.positions.short_entry_leverage,
                    self.positions.short_entry_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Leverage', 'Fee'],
                    [Settings.precision_price, Settings.precision_money,
                     Settings.precision_quantity, None, Settings.precision_fee],
                ),
            ),
        )

        adjust_long_y = self.candles.low_prices if is_candlestick else self.candles.close_prices
        adjust_long_y = adjust_long_y[self.long_adjust_indexes]
        self.graph_objects.append(
            self.__create_marker(
                name='Long adjust',
                x=self.positions.long_adjust_time,
                y=adjust_long_y - np.sqrt(adjust_long_y) * 2.,
                color=long_adjust_marker_color,
                symbol='diamond-tall',
                text=['Adjust'] * len(self.positions.long_adjust_time) if side_labels else None,
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.long_adjust_price,
                    self.positions.long_adjust_amount,
                    self.positions.long_adjust_quantity,
                    self.positions.long_adjust_leverage,
                    self.positions.long_adjust_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Leverage', 'Fee'],
                    [Settings.precision_price, Settings.precision_money,
                     Settings.precision_quantity, None, Settings.precision_fee],
                )
            )
        )

        adjust_short_y = self.candles.low_prices if is_candlestick else self.candles.close_prices
        adjust_short_y = adjust_short_y[self.short_adjust_indexes]
        self.graph_objects.append(
            self.__create_marker(
                name='Short adjust',
                x=self.positions.short_adjust_time,
                y=adjust_short_y - np.sqrt(adjust_short_y) * 2.,
                color=short_adjust_marker_color,
                symbol='diamond-tall',
                text=['Adjust'] * len(self.positions.short_adjust_time) if side_labels else None,
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.short_adjust_price,
                    self.positions.short_adjust_amount,
                    self.positions.short_adjust_quantity,
                    self.positions.short_adjust_leverage,
                    self.positions.short_adjust_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Leverage', 'Fee'],
                    [Settings.precision_price, Settings.precision_money,
                     Settings.precision_quantity, None, Settings.precision_fee],
                )
            )
        )

        long_close_y = self.candles.high_prices if is_candlestick else self.candles.close_prices
        long_close_y = long_close_y[self.long_close_indexes]
        self.graph_objects.append(
            self.__create_marker(
                x=self.positions.long_close_time,
                y=long_close_y + np.sqrt(long_close_y) * 2.,
                name='Long close',
                color=long_exit_marker_color,
                symbol='triangle-down',
                text=['X Long'] * len(self.positions.long_close_time) if side_labels else None,
                text_position='top center',
                customdata=self._create_custom_data(
                    self.positions.long_close_price,
                    self.positions.long_close_profit,
                    self.positions.long_close_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Profit', 'Fee'],
                    [Settings.precision_profit, Settings.precision_profit, Settings.precision_fee]
                )
            )
        )

        short_close_y = self.candles.high_prices if is_candlestick else self.candles.close_prices
        short_close_y = short_close_y[self.short_close_indexes]
        self.graph_objects.append(
            self.__create_marker(
                x=self.positions.short_close_time,
                y=short_close_y + np.sqrt(short_close_y) * 2.,
                name='Short close',
                color=short_close_marker_color,
                symbol='triangle-down',
                text=['X Short'] * len(self.positions.short_close_time) if side_labels else None,
                text_position='top center',
                customdata=self._create_custom_data(
                    self.positions.short_close_price,
                    self.positions.short_close_profit,
                    self.positions.short_close_fee,
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Profit', 'Fee'],
                    [Settings.precision_profit, Settings.precision_profit, Settings.precision_fee]
                )
            )
        )

        if price_markers:
            self.graph_objects.append(
                self.__create_marker(
                    x=self.positions.entry_time,
                    y=self.positions.entry_price,
                    name='Entry price',
                    color=entry_price_marker_color,
                    symbol='arrow-right',
                )
            )

            self.graph_objects.append(
                self.__create_marker(
                    x=self.positions.adjust_time,
                    y=self.positions.adjust_price,
                    name='Adjust price',
                    color=adjust_price_marker_color,
                    symbol='diamond-wide',
                )
            )

            self.graph_objects.append(
                self.__create_marker(
                    x=self.positions.close_time,
                    y=self.positions.close_price,
                    name='Exit price',
                    color=close_price_marker_color,
                    symbol='arrow-left',
                )
            )

        if annotation:
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'ATH: {fmt.num(self.candles.ath(), prec=Settings.precision_price)}',
                        f'ATL: {fmt.num(self.candles.atl(), prec=Settings.precision_price)}',
                    ]),
                    align='left',
                    xref='x domain', yref='y domain',
                    font=dict(size=8),
                    x=0.005, y=0.99, showarrow=False,
                    row=self._graph_counter, col=1,
                )
            )

        self.candlestick_graph = True
        self.candlestick_graph_number = self._graph_counter

    def add_volume_graph(
            self,
            volume_type=Volume.AUTO,
            volume_color='#1f8c1f',
    ):
        if volume_type is Volume.AUTO:
            if len(self.candles) > self.OPTIMIZE_GRAPH_THRESHOLD:
                volume_type = Volume.LINE
            else:
                volume_type = Volume.BAR

        trace = self._scatter if volume_type == Volume.LINE else go.Bar
        self.graph_objects.append(
             dict(
                 trace=trace(
                     x=self.candles.times,
                     y=self.candles.volumes,
                     name=f'Volume ({volume_type})',
                     marker={'color': volume_color},
                     opacity=0.2,
                     hoverinfo='skip',
                 ),
                 secondary_y=True,
                 row=self._graph_counter, col=1,
             )
         )

    def _get_graph_number(self, graph: Graph):
        if graph == Graph.CAPITAL:
            return self.capital_graph_number
        elif graph == Graph.CANDLESTICK:
            return self.candlestick_graph_number
        elif graph == Graph.PROFIT:
            return self.profit_graph_number
        elif graph == Graph.NEW:
            self._graph_counter += 1
            return self._graph_counter

    def add_graphs(self, graph_wrappers: Iterable[CustomGraph]):

        def add_graph(graph_object: go.BaseTraceType, graph_number: int):
            if hasattr(graph_object, 'x') and graph_object.x is None:
                graph_object.x = self.candles.times

            if hasattr(graph_object, 'y') and len(graph_object.y) == 1 and isinstance(graph_object.y[0], float):
                graph_object.y = [graph_object.y[0] for _ in range(len(self.candles))]

            self.graph_objects.append(
                dict(
                    trace=graph_object,
                    row=graph_number,
                    col=1,
                )
            )

        for graph_wrapper in graph_wrappers:
            graph_number = self._get_graph_number(graph=graph_wrapper.graph)

            if isinstance(graph_wrapper.graph_objects, (list, tuple, set, np.ndarray)):
                for graph_object in graph_wrapper.graph_objects:
                    add_graph(graph_object, graph_number)
            else:
                add_graph(graph_wrapper.graph_objects, graph_number)

    def create_figure(self):
        number_of_plots = len(set(graph['row'] for graph in self.graph_objects))

        specs = [[{'secondary_y': True}] for _ in range(number_of_plots)]

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
