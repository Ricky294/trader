"""Shows implementations and charts of candlestick patterns."""
import numpy as np

from examples.candlestick_patterns import plot_candlesticks
from trader.core.util.vectorized.candlestick import bullish_engulfing

o = np.array([175.47, 171.61, 175.69, 181.74, 170.92, 187.07, 174.15, 175.47, 171.61, 175.69, 181.74, 170.92])
h = np.array([184.68, 184.39, 179.22, 183.49, 182.87, 190.78, 196.48, 184.68, 184.39, 179.22, 183.49, 182.87])
l = np.array([169.16, 169.78, 166.80, 171.63, 170.10, 176.94, 170.13, 169.16, 169.78, 166.80, 171.63, 170.10])
c = np.array([169.30, 182.14, 176.60, 177.66, 170.70, 177.32, 192.34, 169.30, 182.14, 176.60, 177.66, 170.70])
eng = bullish_engulfing(o, h, l, c)

plot_candlesticks(
    x=np.arange(o.size),
    open=o,
    high=h,
    low=l,
    close=c,
    bool_arr=eng,
    name="Bullish engulfing candle",
)
