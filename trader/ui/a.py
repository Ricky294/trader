from dash import Dash, dash_table
import pandas as pd

from trader.backtest.model import BacktestPosition
from trader.core.const.trade_actions import BUY, SELL
from trader.core.model import Position, Positions
import plotly.graph_objects as go


def create_dash_datatable(positions: Positions):
    return dash_table.DataTable(
        positions.to_records("pd"),
        columns=[{"name": i, "id": i} for i in positions.columns]
    )


def create_plotly_table(positions: Positions):
    return go.Table(
        header=dict(values=positions.columns),
        cells=dict(values=positions.to_list())
    )


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

pos1 = BacktestPosition("BTCUSDT", 100, BUY, 1, entry_time=2, entry_price=200, entry_fee=0.0002)
pos1.set_exit(time=5, price=200, fee=0.0002)

pos2 = BacktestPosition("BTCUSDT", 200, SELL, 1, entry_time=8, entry_price=250, entry_fee=0.0002)
pos2.set_exit(time=12, price=500, fee=0.0002)

positions = Positions([pos1, pos2])
"""
fig = go.Figure(create_plotly_table(positions))
fig.show()
"""


app = Dash(__name__)

app.layout = create_dash_datatable(positions)

if __name__ == '__main__':
    app.run_server(debug=True)
