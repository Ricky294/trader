import numpy as np

from examples.candlestick_patterns import plot_candlesticks
from trader.core.util.vectorized.candlestick import bullish_three_line_strike, bearish_three_line_strike

o = np.array([8,   6,   4,   2,   10,  12])
h = np.array([9,   7,   5,   11,  14,  17])
l = np.array([6,   4,   2,   1,   3,   8])
c = np.array([7.5, 5.5, 3.5, 10,  12,  15])

butls = bullish_three_line_strike(o, h, l, c)

plot_candlesticks(
    x=np.arange(o.size),
    open=o,
    high=h,
    low=l,
    close=c,
    bool_arr=butls,
    name="Bullish three line strike",
)


o = np.array([3.5, 5.5, 7.5, 7.5,  2,   5])
h = np.array([5.5, 7,   9,   9,    6,   8])
l = np.array([2,   4,   6,   1,    1,   3])
c = np.array([4,   6,   8,   1.5,  5,   6])

betls = bearish_three_line_strike(o, h, l, c)

plot_candlesticks(
    x=np.arange(o.size),
    open=o,
    high=h,
    low=l,
    close=c,
    bool_arr=betls,
    name="Bearish three line strike",
)
