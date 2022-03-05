from typing import Iterable

import dash
import dash_bootstrap_components as dbc
from dash import html, Output, Input
from dash.development.base_component import Component
import dash_daq as daq

from trader.core.util.common import space_by_capital, get_concrete_class_init_params
from trader.core.util.ui import python_type_to_html_input_type

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY, dbc.icons.BOOTSTRAP])


def create_input(label: str, components: Iterable[Component]):
    return dbc.Row([
        dbc.Label(label, width=dict(size=2)),
        dbc.Col(components),
    ], className="mb-3")


def create_static_layout():
    return [
        html.Br(),
        create_input("Symbol", [dbc.Input(id="symbol", type="text", placeholder="e.g. BTCUSDT...")]),
        create_input("Interval", [
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("Minutes", header=True),
                    dbc.DropdownMenuItem("1 minute", id="1m"),
                    dbc.DropdownMenuItem("3 minute", id="3m"),
                    dbc.DropdownMenuItem("5 minutes", id="5m"),
                    dbc.DropdownMenuItem("15 minutes", id="15m"),
                    dbc.DropdownMenuItem("30 minutes", id="30m"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Hours", header=True),
                    dbc.DropdownMenuItem("1 hour", id="1h"),
                    dbc.DropdownMenuItem("2 hours", id="2h"),
                    dbc.DropdownMenuItem("4 hours", id="4h"),
                    dbc.DropdownMenuItem("6 hours", id="6h"),
                    dbc.DropdownMenuItem("8 hours", id="8h"),
                    dbc.DropdownMenuItem("12 hours", id="12h"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Days", header=True),
                    dbc.DropdownMenuItem("1 day", id="1d"),
                    dbc.DropdownMenuItem("3 days", id="3d"),
                ],
                label="Select interval",
                id="interval"
            ),
        ]),
        create_input("Data feed", [
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("Binance", id="feed_binance")
                ],
                label="Select data feed",
                id="data_feed"
            ),
        ]),
        create_input(
            "Store in local database",
            [
                daq.BooleanSwitch(id='switch_db', on=False, color="#4374BA", style={"position": "absolute"}),
            ]
        ),
        dbc.Input(id="input_db", type="text", placeholder="Enter absolute or relative path...", className="mb-3"),
        create_input("Mode", [
            dbc.DropdownMenu(
                [
                    dbc.DropdownMenuItem("Backtest", id="mode_backtest"),
                    dbc.DropdownMenuItem("Binance", id="mode_binance")
                ],
                label="Select mode",
                id="mode"
            )
        ]),
    ]


@app.callback(
    Output('input_db', 'style'),
    Input('switch_db', 'on')
)
def update_output(on):
    return {'display': 'block'} if on else {'display': 'none'}


@app.callback(
    Output("interval", "label"),
    [
        Input("1m", "n_clicks"), Input("3m", "n_clicks"), Input("5m", "n_clicks"),
        Input("15m", "n_clicks"), Input("30m", "n_clicks"),

        Input("1h", "n_clicks"), Input("2h", "n_clicks"), Input("4h", "n_clicks"),
        Input("6h", "n_clicks"), Input("8h", "n_clicks"), Input("12h", "n_clicks"),

        Input("1d", "n_clicks"), Input("3d", "n_clicks"),
    ],
)
def update_interval_dropdown_label(
        min1, min3, min5, min15, min30,
        hour1, hour2, hour4, hour6, hour8, hour12,
        day1, day3
):

    id_lookup = {
        "1m": "1 Minute", "3m": "3 Minutes", "5m": "5 Minutes", "15m": "15 Minutes", "30m": "30 Minutes",
        "1h": "1 Hour", "2h": "2 Hours", "4h": "4 Hours", "6h": "6 Hours", "8h": "8 Hours", "12h": "12 Hours",
        "1d": "1 Day", "3d": "3 Days"
    }

    ctx = dash.callback_context

    if not ctx.triggered:
        return "Select interval"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return id_lookup[button_id]


@app.callback(
    Output("data_feed", "label"),
    [
        Input("feed_binance", "n_clicks")
    ],
)
def update_data_feed_dropdown_label(binance):
    id_lookup = {
        "feed_binance": "Binance",
    }

    ctx = dash.callback_context

    if not ctx.triggered:
        return "Select data feed"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return id_lookup[button_id]


@app.callback(
    Output("mode", "label"),
    [
        Input("mode_backtest", "n_clicks"),
        Input("mode_binance", "n_clicks"),
    ],
)
def update_mode_dropdown_label(backtest, binance):
    id_lookup = {
        "mode_backtest": "Backtest",
        "mode_binance": "Binance",
    }

    ctx = dash.callback_context

    if not ctx.triggered:
        return "Select mode"

    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return id_lookup[button_id]


def create_strategy_layout(strategy_info):
    def convert_to_id(txt):
        return space_by_capital(txt).lower().replace(" ", "_")

    def convert_to_title(txt):
        return space_by_capital(txt)

    return [
        html.Br(),
        html.H3("Select strategy"),
        dbc.Accordion([
            dbc.AccordionItem(
                [
                    create_input(params[0].replace("_", " ").capitalize(), [
                        dbc.Input(
                            id=convert_to_id(name) + "_" + convert_to_id(params[0]),
                            type=python_type_to_html_input_type(params[1]),
                        )
                    ])
                    for params in param_list
                ],
                id=convert_to_id(name),
                title=convert_to_title(name),
            ) for name, param_list in strategy_info.items()
        ], active_item=None),
    ]


def create_indicator_layout():
    return [
        html.Br(),
        html.H3("Select indicator"),
    ]


def create_app(strategy_module: str, indicator_module: str):
    strategy_info = get_concrete_class_init_params(strategy_module)
    indicator_info = get_concrete_class_init_params(indicator_module)

    for param_list in strategy_info.values():
        for name_type_list in param_list:
            if len(name_type_list) == 1:
                name_type_list.append("str")

    app.layout = dbc.Container([
        html.Br(),
        html.H2("Configure trading bot"),
        *create_static_layout(),
        *create_strategy_layout(strategy_info)
    ])

    return app
