import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from trader.data.util import blend_ohlc


def add_example(num, row, col, o, h, l, c):

    o_, h_, l_, c_ = blend_ohlc(o, h, l, c)
    fig.add_trace(
        trace=go.Candlestick(
            name=f"Example {num}",
            x=[1, 2, 3],
            open=np.append(o, o_[-1]),
            high=np.append(h, h_[-1]),
            low=np.append(l, l_[-1]),
            close=np.append(c, c_[-1]),
        ),
        row=row, col=col,
    )

    fig.add_annotation(
        text="+",
        xref="paper", yref="paper",
        x=1.5, y=5, showarrow=False,
        row=row, col=col, font=dict(size=24),
    )
    fig.add_annotation(
        text="=",
        xref="paper", yref="paper",
        x=2.5, y=5, showarrow=False,
        row=row, col=col, font=dict(size=24),
    )


if __name__ == "__main__":

    fig = make_subplots(
        rows=2, cols=2,
        horizontal_spacing=0.025,
        vertical_spacing=0.05,
    )

    add_example(
        num=1,
        row=1, col=1,
        o=np.array([2, 8.2]),
        h=np.array([8, 9]),
        l=np.array([1, 3]),
        c=np.array([8, 4]),
    )

    add_example(
        num=2,
        row=1, col=2,
        o=np.array([2, 5]),
        h=np.array([9, 8]),
        l=np.array([1, 4]),
        c=np.array([5, 7]),
    )

    add_example(
        num=3,
        row=2, col=1,
        o=np.array([5,   1]),
        h=np.array([5.2, 8]),
        l=np.array([2.8, 0.5]),
        c=np.array([3,   7]),
    )

    add_example(
        num=4,
        row=2, col=2,
        o=np.array([3,   7]),
        h=np.array([5.2, 8]),
        l=np.array([2.8, 0.5]),
        c=np.array([5,   1]),
    )

    fig.update_xaxes(rangeslider={'visible': False})
    fig.update_layout(title="Candle blending examples", dragmode='pan')
    config = dict({'scrollZoom': True})
    fig.show(config=config)