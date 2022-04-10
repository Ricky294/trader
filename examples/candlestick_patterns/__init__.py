import plotly.graph_objects as go


def plot_candlesticks(x, open, high, low, close, bool_arr, name):
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=x,
                open=open,
                high=high,
                low=low,
                close=close,
            ),
            go.Scatter(
                x=x,
                y=high * 1.02,
                mode="text",
                name=name,
                text=[name if e else "" for e in bool_arr]
            )
        ],
    )
    fig.update_xaxes(rangeslider={'visible': False})
    fig.show()
