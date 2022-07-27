"""Shows implementations and charts of candlestick patterns."""
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from trader.data.super_enum import Market
from trader.data.binance import get_candles_as_array
from trader.data.util import blend_ohlc


def add_candlestick_chart(name, open, high, low, close, row, col):
    fig.add_trace(
        trace=go.Candlestick(
            name=name,
            x=np.arange(o.size),
            open=open,
            high=high,
            low=low,
            close=close,
        ),
        row=row, col=col,
    )


if __name__ == "__main__":
    candles = get_candles_as_array(
        symbol="BTCUSDT",
        interval="4h",
        market=Market.SPOT,
        start_ts=1640991600,
        end_ts=1643670000
    ).T

    o = candles[1]
    h = candles[2]
    l = candles[3]
    c = candles[4]

    o_, h_, l_, c_ = blend_ohlc(o, h, l, c, period=2)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        horizontal_spacing=0.0,
        vertical_spacing=0.02,
    )

    add_candlestick_chart(
        name="Japanase candles",
        open=o,
        high=h,
        low=l,
        close=c,
        row=1, col=1,
    )

    add_candlestick_chart(
        name="Blended candles",
        open=o_,
        high=h_,
        low=l_,
        close=c_,
        row=2, col=1,
    )

    fig.update_xaxes(rangeslider={'visible': False})
    fig.update_layout(dragmode='pan')
    config = dict({'scrollZoom': True})
    fig.show(config=config)
