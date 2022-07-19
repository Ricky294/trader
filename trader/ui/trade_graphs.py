from __future__ import annotations

from typing import Iterable

import numpy as np
import nputils as npu
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from trader.core.const.trade_actions import LONG, SHORT
from trader.core.enumerate import SideFormat
from trader.core.model.balances import Balances
from trader.core.model.fees import Fees
from trader.core.util.trade import format_side
from trader.data.model import Candles

from trader.config import (
    BALANCE_PRECISION,
    FEE_PRECISION,
    MONEY_PRECISION,
    PRICE_PRECISION,
    PROFIT_PRECISION,
    QUANTITY_PRECISION
)
import trader.core.indicator as ind
import trader.core.util.format as fmt
from trader.core.model import Positions

from trader.ui import CustomGraph
from trader.ui.enumerate import Candlestick, Volume, Graph


class TradeGraphs:

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

    @staticmethod
    def _create_full_series(time_series, positions: Positions, fees: Fees, start_cash: float):
        entry_time = npu.replace_where_not_found(time_series, positions.entry_time, 0)
        entry_fee = npu.replace_where(entry_time, entry_time != 0, fees.entry_fee)

        exit_time = npu.replace_where_not_found(time_series, positions.exit_time, 0)
        exit_fee = npu.replace_where(exit_time, exit_time != 0, fees.exit_fee)

        if len(positions.profit) != len(exit_time[exit_time != 0]):
            profit = positions.profit[:-1]
        else:
            profit = positions.profit

        profit = npu.replace_where(exit_time, exit_time != 0, profit)

        cum_fee = np.cumsum(entry_fee + exit_fee)
        cum_capital = np.cumsum(profit) + start_cash - cum_fee

        return cum_fee, cum_capital

    def __init__(
            self,
            candles: Candles,
            positions: Positions,
            balances: Balances,
            fees: Fees,
            web_gl=True,
    ):
        self.web_gl = web_gl
        if web_gl:
            self._scatter = go.Scattergl
        else:
            self._scatter = go.Scatter

        self.candles = candles
        self.balances = balances
        self.start_cash = balances.balance[0]

        self.fees = fees

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
        self.cum_fee, self.cum_capital = self._create_full_series(candles.times, positions, fees, self.start_cash)

        # https://stackoverflow.com/questions/33678543/finding-indices-of-matches-of-one-array-in-another-array
        self.entry_indexes = np.nonzero(np.isin(self.candles.times, positions.entry_time))[0]
        self.long_entry_indexes = np.nonzero(np.isin(self.candles.times, positions.long_entry_time))[0]
        self.short_entry_indexes = np.nonzero(np.isin(self.candles.times, positions.short_entry_time))[0]

        self.exit_indexes = np.nonzero(np.isin(self.candles.times, positions.exit_time))[0]
        self.long_exit_indexes = np.nonzero(np.isin(self.candles.times, positions.long_exit_time))[0]
        self.short_exit_indexes = np.nonzero(np.isin(self.candles.times, positions.short_exit_time))[0]

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
                    x=self.candles.pd_open_times,
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
                        x=self.candles.pd_open_times,
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
            final_balance = float(self.cum_capital[-1])
            total_profit = (final_balance - self.start_cash) / self.start_cash
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'Start balance: {fmt.num(self.start_cash, BALANCE_PRECISION)} ',
                        f'Final balance: {fmt.num(final_balance, BALANCE_PRECISION)} '
                        f'({fmt.num(total_profit, PROFIT_PRECISION, perc=True, plus=True)})',
                        f'Total paid fee: {fmt.num(self.cum_fee[-1], FEE_PRECISION)}',
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

        positive_profit_marker_size = np.absolute(apply_logarithm(self.positions.positive_profit))
        negative_profit_marker_size = np.absolute(apply_logarithm(self.positions.negative_profit))

        self.graph_objects.append(
            dict(
                trace=go.Scatter(
                    x=pd.to_datetime(self.positions.positive_profit_time, unit='s'),
                    y=self.positions.positive_profit,
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
                    x=pd.to_datetime(self.positions.negative_profit_time, unit='s'),
                    y=self.positions.negative_profit,
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

        if annotation:
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'Wins: {self.positions.number_of_wins}, Losses: {self.positions.number_of_losses}, '
                        f'Win rate: {fmt.num(self.positions.win_rate, 3, perc=True)}',
                        f'Largest win: {fmt.num(self.positions.largest_profit, PROFIT_PRECISION, plus=True)} '
                        f'Largest loss: {fmt.num(self.positions.largest_loss, PROFIT_PRECISION)}',
                        f'Average win/loss: {fmt.num(self.positions.average_profit_and_loss, PROFIT_PRECISION, plus=True)}',
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
                x=pd.to_datetime(x, unit='s'),
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
            candlestick_type=Candlestick.LINE,
            long_entry_marker_color='#3d8f6d',
            short_entry_marker_color='red',
            long_exit_marker_color='#3d8f6d',
            short_exit_marker_color='red',
            entry_price_marker_color='#2871cc',
            annotation=True,
    ):
        candle_len = len(self.candles)
        hover_text = np.array([f'count: {fmt.num(i + 1)}/{fmt.num(candle_len)}' for i in range(candle_len)])

        def append_candlestick_graph(candles: Candles):
            self.graph_objects.append(
                dict(
                    trace=go.Candlestick(
                        x=candles.pd_open_times,
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
                        x=self.candles.pd_open_times,
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
                text=[fmt.capitalize(format_side(long, SideFormat.LONG_SHORT)) for long in self.positions.long_side],
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.long_entry_price,
                    self.positions.long_money,
                    self.positions.long_quantity,
                    self.fees.entry_fee[self.positions.side == LONG]
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Fee'],
                    [PRICE_PRECISION, MONEY_PRECISION, QUANTITY_PRECISION, FEE_PRECISION],
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
                text=[fmt.capitalize(format_side(short, SideFormat.LONG_SHORT)) for short in self.positions.short_side],
                text_position='bottom center',
                customdata=self._create_custom_data(
                    self.positions.short_entry_price,
                    self.positions.short_money,
                    self.positions.short_quantity,
                    self.fees.entry_fee[self.positions.side == SHORT]
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Money', 'Quantity', 'Fee'],
                    [PRICE_PRECISION, MONEY_PRECISION, QUANTITY_PRECISION, FEE_PRECISION],
                ),
            ),
        )

        if len(self.fees.exit_fee) != len(self.positions.side):
            side = self.positions.side[:-1]
        else:
            side = self.positions.side

        if len(self.positions.long_exit_time) > 0 and self.positions.long_exit_time[-1] is None:
            long_exit_time = self.positions.long_exit_time[:-1]
            long_exit_price = self.positions.long_exit_price[:-1]
            long_profit = self.positions.long_profit[:-1]
        else:
            long_exit_time = self.positions.long_exit_time
            long_exit_price = self.positions.long_exit_price
            long_profit = self.positions.long_profit

        if len(self.positions.short_exit_time) > 0 and self.positions.short_exit_time[-1] is None:
            short_exit_time = self.positions.short_exit_time[:-1]
            short_exit_price = self.positions.short_exit_price[:-1]
            short_profit = self.positions.short_profit[:-1]
        else:
            short_exit_time = self.positions.short_exit_time
            short_exit_price = self.positions.short_exit_price
            short_profit = self.positions.short_profit

        long_exit_y = self.candles.high_prices if is_candlestick else self.candles.close_prices
        long_exit_y = long_exit_y[self.long_exit_indexes]
        self.graph_objects.append(
            self.__create_marker(
                x=long_exit_time,
                y=long_exit_y + np.sqrt(long_exit_y) * 2.,
                name='Long exit',
                color=long_exit_marker_color,
                symbol='triangle-down',
                text=[
                    f'X {fmt.capitalize(format_side(side, SideFormat.LONG_SHORT))}'
                    for side in self.positions.long_side
                ],
                text_position='top center',
                customdata=self._create_custom_data(
                    long_exit_price,
                    long_profit,
                    self.fees.exit_fee[side == LONG]
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Profit', 'Fee'],
                    [PROFIT_PRECISION, PROFIT_PRECISION, FEE_PRECISION]
                )
            )
        )

        short_exit_y = self.candles.high_prices if is_candlestick else self.candles.close_prices
        short_exit_y = short_exit_y[self.short_exit_indexes]
        self.graph_objects.append(
            self.__create_marker(
                x=short_exit_time,
                y=short_exit_y + np.sqrt(short_exit_y) * 2.,
                name='Short exit',
                color=short_exit_marker_color,
                symbol='triangle-down',
                text=[f'X {fmt.capitalize(format_side(side, SideFormat.LONG_SHORT))}' for side in self.positions.short_side],
                text_position='top center',
                customdata=self._create_custom_data(
                    short_exit_price,
                    short_profit,
                    self.fees.exit_fee[side == SHORT]
                ),
                hovertemplate=self._create_hover_template(
                    ['Price', 'Profit', 'Fee'],
                    [PROFIT_PRECISION, PROFIT_PRECISION, FEE_PRECISION]
                )
            )
        )

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
                x=self.positions.exit_time,
                y=self.positions.exit_price,
                name='Exit price',
                color=entry_price_marker_color,
                symbol='arrow-left',
            )
        )

        if annotation:
            self.annotations.append(
                dict(
                    text='<br>'.join([
                        f'ATH: {fmt.num(self.candles.ath(), PRICE_PRECISION)}',
                        f'ATL: {fmt.num(self.candles.atl(), PRICE_PRECISION)}',
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
            volume_type=Volume.LINE,
            volume_color='#2CA02C',
    ):
        trace = self._scatter if volume_type == Volume.LINE else go.Bar
        self.graph_objects.append(
             dict(
                 trace=trace(
                     x=self.candles.pd_open_times,
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
                        trace=self._scatter(
                            x=self.candles.pd_open_times,
                            y=y_data,
                            name=fmt.capitalize(name),
                        ),
                        row=figure_number, col=1,
                    )
                )
            elif 'limit' in name and isinstance(y_data, (float, int)):
                self.graph_objects.append(
                    dict(
                        trace=self._scatter(
                            x=[self.candles.pd_open_times[0], self.candles.pd_open_times[-1]],
                            y=[y_data, y_data],
                            mode='lines',
                            hoverinfo='skip',
                            marker=dict(color='#187bcd'),
                            name=fmt.capitalize(name, y_data),
                        ),
                        row=figure_number, col=1,
                    )
                )

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
