from datetime import date, datetime
from typing import Iterable

import plotly.graph_objects as go
from dash import Dash, html, dcc, Input, Output, callback_context, State
import dash_bootstrap_components as dbc

from trader.core.model import Position, Positions

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True,)


def create_interval_label():
    return dbc.Col(html.P("Interval", style={"margin-top": "0.75em"}), width=1)


def create_interval_selector(intervals: Iterable[str]):
    return dbc.Col(
        dbc.RadioItems(
            id="intervals",
            className="btn-group",
            inputClassName="btn-check",
            labelClassName="btn btn-outline-primary",
            labelCheckedClassName="active",
            options=[{"label": e, "value": e} for e in intervals],
            value=None,
        ),
        className="radio-group",
    )


def create_date_label():
    return dbc.Col(html.P("Date", style={"margin-top": "0.75em"}), width=1)


def create_date_picker(min_date: date, end_date: date):
    return dbc.Col(
        dcc.DatePickerRange(
            id="date_picker",
            minimum_nights=1,
            min_date_allowed=min_date,
            max_date_allowed=end_date,
            start_date=min_date,
            end_date=end_date,
            style={
                'font-size': '0.9em',
                'display': 'inline-block',
                'border-radius': '10px',
                'color': '#333',
                'border-spacing': '0',
                'border-collapse': 'separate'
            }
        ), width="auto",
    )


def create_quick_date_group():
    return dbc.Col(
        dbc.ButtonGroup(
            id="quick_date",
            children=[
                dbc.Button(
                    id=f"date_{e}",
                    children=e,
                    n_clicks=0,
                    style={
                        "textAlign": "center",
                        "font-size": "0.8em",
                        "background-color": "transparent",
                        "border-color": "transparent",
                        "color": "black",
                    },
                )
                for e in ["1M", "2M", "3M", "6M", "1Y", "MAX"]
            ]
        ), width="auto", style={"margin-top": "0.5em"},
    )


@app.callback(
    Output('tab_content', 'children'),
    Input('tabs', 'value'),
)
def tab_content(tab):
    if tab == 'graphs_tab':
        return html.Div([
            dcc.Graph(
                id='graphs',
                figure={},
                style=dict(width='97.66vw', height='95vh'),
                config=dict(scrollZoom=True),
            )
        ])
    elif tab == 'positions_tab':
        return html.Div([
            dcc.Graph(
                id='positions',
                figure=go.Figure(
                    data=[
                        go.Table()
                    ]
                ),
                style=dict(width='97.66vw', height='95vh'),
            ),
        ])
    elif tab == "stats_tab":
        return "Stats tab"
    elif tab == "orders_tab":
        return "Orders tab"


@app.callback(
    Output("graphs", "figure"),
    Input("run_btn", "n_clicks"),
    State("date_picker", "start_date"),
    State("date_picker", "end_date"),
    State("intervals", "value"),
    prevent_initial_call=True,
)
def run(click, start_date, end_date, interval):
    print(click)
    print(start_date)
    print(end_date)
    print(interval)


@app.callback(
    Output("date_picker", "start_date"),
    Output("date_picker", "end_date"),
    Input("date_1M", "n_clicks"),
    Input("date_2M", "n_clicks"),
    Input("date_3M", "n_clicks"),
    Input("date_6M", "n_clicks"),
    Input("date_1Y", "n_clicks"),
    Input("date_MAX", "n_clicks"),
    prevent_initial_call=True,
)
def set_date(m1, m2, m3, m6, y1, max_):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    now = datetime.now().timestamp()
    end_date = date.fromtimestamp(now)

    month_in_sec = 2629800
    start_ts = now - month_in_sec

    if 'date_1M' in changed_id:
        start_ts = now - month_in_sec
    elif 'date_2M' in changed_id:
        start_ts = now - (month_in_sec * 2)
    elif 'date_3M' in changed_id:
        start_ts = now - (month_in_sec * 3)
    elif 'date_6M' in changed_id:
        start_ts = now - (month_in_sec * 6)
    elif 'date_1Y' in changed_id:
        start_ts = now - (month_in_sec * 12)
    elif 'date_MAX' in changed_id:
        start_ts = 1

    start_date = date.fromtimestamp(start_ts)
    return start_date, end_date


def create_stat_cards(stats: dict[str, str]):
    return [
        dbc.Col(create_stat_card(title, value), style={"margin-bottom": "1vh"}, width="auto")
        for title, value in stats.items()
    ]


def create_stat_card(title: str, value: str):
    return dbc.Card(
        dbc.CardBody(
            [
                html.H6(title, className="stat_card_title"),
                html.H5(value, className="stat_card_value"),
            ]
        ),
        className="stat_card",
    )


def create_run_button():
    return dbc.Button(
        id="run_btn",
        children="Run",
        n_clicks=0,
        style={
            "margin-top": "0.5vh",
        },
    )


def layout(
        positions: Iterable[Position],
        intervals: Iterable[str],
        stats: dict[str, str],
        min_date: date,
        end_date=datetime.now().date(),
):
    positions = Positions(positions)

    date_row = dbc.Row([
        create_date_label(),
        create_date_picker(min_date=min_date, end_date=end_date),
        create_quick_date_group()
    ])

    interval_row = dbc.Row([
        create_interval_label(),
        create_interval_selector(intervals),
    ])

    settings_card = dbc.Card(
        dbc.CardBody(
            [
                date_row,
                interval_row,
                create_run_button(),
            ],
            id="config",
        ),
        style={"margin-bottom": "1vh"},
    )

    stat_cards = dbc.Row(create_stat_cards(stats))

    return html.Div(children=[
        dcc.Tabs(id="tabs", value='graphs_tab', children=[
            dcc.Tab(label='Graphs', value='graphs_tab'),
            dcc.Tab(label='Stats', value='stats_tab'),
            dcc.Tab(label='Positions', value='positions_tab'),
            dcc.Tab(label='Orders', value='orders_tab'),
        ]),
        html.Div(
            id="content",
            style={"margin": "1vh 1vw 1vh 1vw"},
            children=[
                settings_card,
                stat_cards,
                html.Div(id="tab_content"),
            ],
        ),
    ])


intervals = "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"
app.layout = layout(
    intervals=intervals,
    stats={"Maximum drawdown": "14.25%"},
    min_date=date(2010, 1, 1),
    end_date=date(2015, 1, 1),
)
app.run_server(debug=True)
