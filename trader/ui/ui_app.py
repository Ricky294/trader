from __future__ import annotations

from typing import Iterable

import pandas as pd
import dash_bootstrap_components as dbc
from dash import dash_table, Dash, html, dcc, Input, Output

import util.format_util as fmt
from util.inspect_util import is_all_empty

from trader.data.model import Candles, Models

from trader.core.model import Balances, Positions, Orders, POSITION_ENTRY, POSITION_CLOSE

from trader.settings import Settings

from trader.ui import CustomGraph, PlotlyTradeGraphs
from trader.ui.const import Candlestick, Volume


def format_trade(
        model_list: Models,
        exclude: tuple = tuple(),
        exclude_empty=True,
):
    def format_values(name: str, values: Iterable):

        if name in {'balance', 'total', 'available'}:
            prec = Settings.precision_balance
        elif 'fee' in name:
            prec = Settings.precision_fee
        elif 'amount' in name:
            prec = Settings.precision_money
        elif 'price' in name:
            prec = Settings.precision_price
        elif 'profit' in name:
            prec = Settings.precision_profit
        elif 'quantity' in name:
            prec = Settings.precision_quantity
        else:
            return [str(val) for val in values]

        return fmt.num(values, prec=prec)

    fmt_dict = {col: format_values(col, values) for col, values in model_list.to_dict().items() if col not in exclude}

    return (
        {col: data for col, data in fmt_dict.items() if not is_all_empty(data)}
        if exclude_empty
        else fmt_dict
    )


class UIApp:

    def __init__(
            self,
            candles: Candles,
            balances: Balances,
            orders: Orders,
            positions: Positions,
    ):
        self.candles = candles
        self.positions = positions
        self.orders = orders
        self.balances = balances
        self.app = UIApp.create_app()

    @staticmethod
    def create_app():
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        app.layout = html.Div(children=[
            dcc.Tabs(id='tabs', value='charts_tab', children=[
                dcc.Tab(label='Charts', value='charts_tab'),
                dcc.Tab(label='Stats', value='stats_tab'),
                dcc.Tab(label='Equity', value='equity_tab'),
                dcc.Tab(label='Positions', value='positions_tab'),
                dcc.Tab(label='Orders', value='orders_tab'),
            ]),
            html.Div(id='tab_content'),
        ])
        return app

    def run(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type: Volume | None = Volume.LINE,
            side_labels=True,
            price_markers=True,
            custom_graphs: Iterable[CustomGraph] = (),
            debug=False,
    ):

        @self.app.callback(
            Output('tab_content', 'children'),
            Input('tabs', 'value')
        )
        def tab_content(tab):
            view_width = '99vw'
            view_height = '88vh'
            tab_style = dict(width=view_width, height=view_height, position='absolute', left='0.5%', top='10%')
            if tab == 'charts_tab':
                return html.Div([
                    dcc.Graph(
                        id='graphs',
                        style=dict(width=view_width, height=view_height),
                        figure=self._create_trade_graphs(
                            candlestick_type=candlestick_type,
                            side_labels=side_labels,
                            price_markers=price_markers,
                            volume_type=volume_type,
                            custom_graphs=custom_graphs,
                        ),
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
        self.app.run_server(debug=debug)

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
                {
                    'name': 'Total positions',
                    'value': f'{fmt.num(self.positions.number_of_closed_positions)} (closed), '
                             f'{self.positions.number_of_opened_positions - self.positions.number_of_closed_positions} (open)'
                },
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
                    'value': fmt.num(self.positions.largest_profit, prec=Settings.precision_profit, plus=True),
                    'date': largest_profit_date,
                },
                {
                    'name': 'Largest loss',
                    'value': fmt.num(self.positions.largest_loss, Settings.precision_profit),
                    'date': largest_loss_date,
                },
                {'name': 'Average profit', 'value': fmt.num(self.positions.average_profit, Settings.precision_profit, plus=True)},
                {'name': 'Average loss', 'value': fmt.num(self.positions.average_loss, Settings.precision_profit)},
                {'name': 'Sum P&L', 'value': fmt.num(self.positions.sum_profit_and_loss, Settings.precision_profit)},
                # {'name': 'Annual P&L', 'value': fmt.num()}
                {'name': "Average P&L / Expectancy", 'value': fmt.num(self.positions.average_profit_and_loss, Settings.precision_profit)},
                {'name': 'Profit factor', 'value': fmt.num(self.positions.profit_factor, Settings.precision_profit)},
                {'name': 'Start balance', 'value': fmt.num(self.balances[0].total, Settings.precision_balance), 'date': self.candles.times[0]},
                {
                    'name': 'End balance',
                    'value': f'{fmt.num(self.balances[-1].total, Settings.precision_balance)} (total), '
                             f'{fmt.num(self.balances[-1].available, Settings.precision_balance)} (available)',
                    'date': self.candles.times[-1]}
            ],
            tooltip_data=[
                {'name': 'Number of opened position.'},
                {'name': 'Number of winning trades - Percentage win rate'},
                {'name': 'Number of loosing trades - Percentage loss rate'},
                {'name': 'Largest profit'},
                {'name': 'Largest loss'},
                {'name': 'Sum of all winning trades / number of wins'},
                {'name': 'Sum of all loosing trades / number of losses'},
                {'name': 'Sum of all winning and loosing trades'},
                {'name': 'Shows the expected profit or loss per trade'},
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
                {'name': fmt.title(name), 'id': name, 'selectable': selectable, 'hideable': hideable}
                for name in df.columns
            ],
            data=df.to_dict('rows'),
            filter_action='native',
            sort_action='native',
            page_size=18,
            page_current=0,
        )

    def _create_equity_table(self):
        formatted_equity = format_trade(self.balances, exclude=('_Model__count', '_Balance__count'))
        equity_df = pd.DataFrame(formatted_equity)

        return self._create_table(equity_df, 'equity_table')

    def _create_positions_table(self):
        formatted_positions = format_trade(self.positions, exclude=('_Model__count', '_Position__count'))
        pos_df = pd.DataFrame(formatted_positions)

        def map_state(state):
            if int(state) == POSITION_ENTRY:
                return 'Entry'
            elif int(state) == POSITION_CLOSE:
                return 'Close'
            return f'Adjust {state}'

        pos_df['state'] = pos_df['state'].apply(map_state)
        return self._create_table(pos_df, 'positions_table')

    def _create_orders_table(self):
        formatted_orders = format_trade(self.orders, exclude=('_Model__count', '_Order__count'))
        ord_df = pd.DataFrame(formatted_orders)

        return self._create_table(ord_df, 'orders_table')

    def _create_trade_graphs(
            self,
            candlestick_type=Candlestick.AUTO,
            volume_type: Volume | None = Volume.AUTO,
            side_labels=True,
            price_markers=True,
            custom_graphs: Iterable[CustomGraph] = (),
    ):
        graphs = PlotlyTradeGraphs(
            candles=self.candles,
            positions=self.positions,
            balances=self.balances,
        )

        graphs.add_capital_graph()
        graphs.add_profit_graph()
        graphs.add_candlestick_graph(
            candlestick_type=candlestick_type,
            side_labels=side_labels,
            price_markers=price_markers,
        )
        if volume_type:
            graphs.add_volume_graph(volume_type)
        graphs.add_graphs(custom_graphs)
        figure = graphs.create_figure()
        return figure
