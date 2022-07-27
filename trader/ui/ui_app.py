from __future__ import annotations

from typing import Iterable

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dash_table, Dash, html, dcc, Input, Output

from trader.core.model.fees import Fees
from trader.core.util.format import title
from trader.data.model import Candles

from trader.config import PROFIT_PRECISION, BALANCE_PRECISION

from trader.core.model.balances import Balances
from trader.core.util import format as fmt
from trader.core.model import Position, Positions, Order, Orders, Balance
from trader.core.indicator import Indicator
from trader.data.model.columnar import format_trade

from trader.ui import CustomGraph, TradeGraphs
from trader.ui.enumerate import Candlestick, Volume


class UIApp:

    def __init__(
            self,
            candles: Candles,
            balances: Iterable[Balance],
            orders: Iterable[Order],
            positions: Iterable[Position],
            entry_fees: Iterable[float],
            exit_fees: Iterable[float],
    ):
        self.candles = candles
        self.positions = Positions(positions)
        self.orders = Orders(orders)
        self.balances = Balances(balances)
        self.fees = Fees(entry_fees, exit_fees)

    @staticmethod
    def _main_layout():
        return html.Div(children=[
            dcc.Tabs(id='tabs', value='graphs_tab', children=[
                dcc.Tab(label='Graphs', value='graphs_tab'),
                dcc.Tab(label='Stats', value='stats_tab'),
                dcc.Tab(label='Equity', value='equity_tab'),
                dcc.Tab(label='Positions', value='positions_tab'),
                dcc.Tab(label='Orders', value='orders_tab'),
            ]),
            # cards,
            html.Div(id='tab_content'),
        ])

    def run(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type=Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = (),
    ):
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        trade_graphs = self._create_trade_graphs(
            candlestick_type=candlestick_type,
            volume_type=volume_type,
            custom_graphs=custom_graphs,
        )
        app.layout = self._main_layout()

        @app.callback(
            Output('tab_content', 'children'),
            Input('tabs', 'value')
        )
        def tab_content(tab):
            view_width = '99vw'
            view_height = '88vh'
            tab_style = dict(width=view_width, height=view_height, position='absolute', left='0.5%', top='10%')
            if tab == 'graphs_tab':
                return html.Div([
                    dcc.Graph(
                        id='graphs',
                        style=dict(width=view_width, height=view_height),
                        figure=trade_graphs,
                        config=dict(scrollZoom=True)
                    )
                ])
            elif tab == 'stats_tab':
                return html.Div(
                    [self._create_stats_table()],
                    id='stats',
                    style=tab_style,
                )
            elif tab == 'equity_tab':
                return html.Div(
                    [self._create_equity_table()],
                    id='equity',
                    style=tab_style,
                )
            elif tab == 'positions_tab':
                return html.Div(
                    [self._create_positions_table()],
                    id='positions',
                    style=tab_style,
                )
            elif tab == 'orders_tab':
                return html.Div(
                    [self._create_orders_table()],
                    id='orders',
                    style=tab_style,
                )

        # This must be called last to avoid bugs!
        app.run_server(debug=True)

    def _create_stats_table(self):
        largest_loss_date = self.positions.largest_loss_date
        largest_loss_date = pd.to_datetime(largest_loss_date, unit='s') if largest_loss_date else '-'
        largest_profit_date = self.positions.largest_profit_date
        largest_profit_date = pd.to_datetime(largest_profit_date, unit='s') if largest_profit_date else '-'

        return dash_table.DataTable(
            id='stats_table',
            columns=[
                {'name': 'Name', 'id': 'name', 'selectable': True},
                {'name': 'Value', 'id': 'value', 'selectable': True},
                {'name': 'Date', 'id': 'date', 'selectable': True}
            ],
            data=[
                {'name': 'Total positions', 'value': fmt.num(self.positions.number_of_trades)},
                {
                    'name': 'Wins - % Win',
                    'value': f'({fmt.num(self.positions.number_of_wins)})'
                             f' {fmt.num(self.positions.win_rate, prec=3, perc=True)}'
                },
                {
                    'name': 'Losses - % Loss',
                    'value': f'({fmt.num(self.positions.number_of_losses)}) '
                             f' {fmt.num(self.positions.loss_rate, prec=3, perc=True)}'
                },
                {
                    'name': 'Largest profit',
                    'value': fmt.num(self.positions.largest_profit, PROFIT_PRECISION, plus=True),
                    'date': largest_profit_date,
                },
                {
                    'name': 'Largest loss',
                    'value': fmt.num(self.positions.largest_loss, PROFIT_PRECISION),
                    'date': largest_loss_date,
                },
                {'name': 'Average profit', 'value': fmt.num(self.positions.average_profit, PROFIT_PRECISION, plus=True)},
                {'name': 'Average loss', 'value': fmt.num(self.positions.average_loss, PROFIT_PRECISION)},
                {'name': 'Sum P&L', 'value': fmt.num(self.positions.sum_profit_and_loss, PROFIT_PRECISION)},
                {'name': "Average P&L / Expectancy", 'value': fmt.num(self.positions.average_profit_and_loss, PROFIT_PRECISION)},
                {'name': 'Profit factor', 'value': fmt.num(self.positions.profit_factor, PROFIT_PRECISION)},
                {'name': 'Start balance', 'value': fmt.num(self.balances.balance[0], BALANCE_PRECISION)},
                {'name': 'End balance', 'value': fmt.num(self.balances.balance[-1], BALANCE_PRECISION)}
            ],
            tooltip_data=[
                {'name': 'Number of trades.'},
                {'name': 'Number of winning trades - Percentage win rate'},
                {'name': 'Number of loosing trades - Percentage loss rate'},
                {'name': 'Largest profit'},
                {'name': 'Largest loss'},
                {'name': 'Sum of all winning trades / number of wins'},
                {'name': 'Sum of all loosing trades / number of losses'},
                {'name': 'Sum of all winning and loosing trades'},
                {'name': 'Show the expected profit or loss per trade'},
                {'name': 'If value is above 1, the expected profit per trade is positive.'}
            ],
            tooltip_delay=200,
            tooltip_duration=None,
        )

    @staticmethod
    def _create_table(df: pd.DataFrame, table_id: str, selectable=True, hideable=True):
        return dash_table.DataTable(
            id=table_id,
            columns=[
                {'name': title(name), 'id': name, 'selectable': selectable, 'hideable': hideable}
                for name in df.columns
            ],
            data=df.to_dict('records'),
            filter_action='native',
            sort_action='native',
            page_size=18,
            page_current=0,
        )

    def _create_equity_table(self):
        formatted_equity = format_trade(self.balances, unit='s')
        equity_df = pd.DataFrame(formatted_equity)

        return self._create_table(equity_df, 'equity_table')

    def _create_positions_table(self):
        formatted_positions = format_trade(self.positions, unit='s')
        pos_df = pd.DataFrame(formatted_positions)

        return self._create_table(pos_df, 'positions_table')

    def _create_orders_table(self):
        formatted_orders = format_trade(self.orders, unit='s')
        ord_df = pd.DataFrame(formatted_orders)

        return self._create_table(ord_df, 'orders_table')

    def _create_trade_graphs(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type=Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = (),
    ):
        graphs = TradeGraphs(
            candles=self.candles,
            positions=self.positions,
            balances=self.balances,
            fees=self.fees
        )

        graphs.add_capital_graph()
        graphs.add_profit_graph()
        graphs.add_candlestick_graph(candlestick_type)
        graphs.add_volume_graph(volume_type)
        graphs.add_graphs(custom_graphs)
        figure = graphs.create_figure()
        return figure
