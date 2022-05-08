from __future__ import annotations

from typing import Iterable

from dash import dash_table
from trader.data.model import Candles

from trader.core.model import Positions
from trader.backtest.model import BacktestPosition
from trader.ui import CustomGraph, TradeGraphs
from trader.ui.enumerate import Candlestick, Volume
from trader.core.indicator import Indicator
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


class UIApp:

    def __init__(self, candles: Candles, positions: Iterable[BacktestPosition], start_cash: float):
        self.candles = candles
        self.positions = Positions(positions)
        self.start_cash = start_cash

    @staticmethod
    def _main_layout():
        return html.Div(children=[
            dcc.Tabs(id="tabs", value='graphs_tab', children=[
                dcc.Tab(label='Graphs', value='graphs_tab'),
                dcc.Tab(label='Stats', value='stats_tab'),
                dcc.Tab(label='Positions', value='positions_tab'),
                dcc.Tab(label='Orders', value='orders_tab'),
            ]),
            # cards,
            html.Div(id="tab_content"),
            dbc.Button(
                id="refresh",
                children="Re-run backtest",
                n_clicks=0,
                style=dict(
                    textAlign="center",
                    margin="10px",
                    # position="absolute",
                    # left="50%",
                ),
            )
        ])

    def run_ui_app(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type=Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = (),
    ):
        app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

        trade_graphs = self._trade_graphs(
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
            if tab == 'graphs_tab':
                return html.Div([
                    dcc.Graph(
                        id='graphs',
                        style=dict(width='99vw', height='95vh'),
                        figure=trade_graphs,
                        config=dict(scrollZoom=True)
                    )
                ])
            elif tab == 'positions_tab':
                return html.Div([
                    dcc.Graph(
                        id='positions',
                        style=dict(width='99vw', height='95vh'),
                        figure=self._positions_table()
                    ),
                ])
            elif tab == "stats_tab":
                return "Stats tab"
            elif tab == "orders_tab":
                return "Orders tab"

        # This must be called last to avoid bugs!
        app.run_server(debug=True)

    def _positions_table(self):
        return dash_table.DataTable(
            self.positions.to_dict()
        )

        return go.Figure(data=[
            go.Table(
                header=dict(values=self.positions.columns()),
                cells=dict(values=self.positions.to_list()),
            ),
        ])

    def _orders_table(self): ...

    def _trade_graphs(
            self,
            candlestick_type=Candlestick.LINE,
            volume_type=Volume.LINE,
            custom_graphs: Iterable[CustomGraph | Indicator] = (),
    ):
        graphs = TradeGraphs(
            candles=self.candles,
            positions=self.positions,
            start_cash=self.start_cash
        )

        graphs.add_capital_graph()
        graphs.add_profit_graph()
        graphs.add_candlestick_graph(candlestick_type, volume_type)
        graphs.add_graphs(custom_graphs)
        figure = graphs.create_figure()
        return figure
