from __future__ import annotations

import numpy as np
import talib

from trader.core.enum import MA
from trader.core.util.vectorized.common import consecutive_increase, consecutive_decrease


def talib_ma(x: np.ndarray, /, type: MA | str, period: int) -> np.ndarray:
    """
    Calculates moving average of `type` on `x` with lookback `period` using TA-Lib.
    """
    return getattr(talib, str(type))(x, timeperiod=period)


def cross(x: np.ndarray, /):
    """
    This function can be used to generate cross signals.

    :param x: boolean numpy array
    :return: boolean numpy array
    :examples:

    >>> cross(np.array([-2, -1, 1, 2, 3]) > 0)
    array([False, False, True, False, False])

    >>> cross(np.array([np.nan, np.nan, 1, -1, 1, 2]) > 0)
    array([False, False, False, False, True, False])

    >>> cross(np.array([1, 2, 3, 4, 5, 6]) <= np.array([0, 2, 4, 1, 2, 8]))
    array([False, True, False, False, False, True])
    """

    mask = np.where(x, True, False)
    sliding_arr = np.lib.stride_tricks.sliding_window_view(mask, 2)
    cross_signal = (sliding_arr[:, 0] == False) & (sliding_arr[:, 1] == True)

    ret = np.insert(cross_signal, 0, False)
    return ret


def slope(y: np.ndarray, period: int):
    """
    Calculates the slope on `y` on a `period` sliding window.

    Calculation formula (applied on every window):
        slope = (x[-1] - x[0]) / period

    :param y: 1D iterable
    :param period: Calculates the slope on every n period.
    :return: numpy array

    :example:
    >>> slope(np.array([1, 2, 4, 8, 16, 32, 64, 128]), period=3)
    array([nan, nan,  1.,  2.,  4.,  8., 16., 32.])
    """

    sliding_arr = np.lib.stride_tricks.sliding_window_view(y, period)
    slope_arr = (sliding_arr[:, period - 1] - sliding_arr[:, 0]) / period

    return np.concatenate((np.full(period - 1, np.nan), slope_arr))


def heikin_ashi_open(open: np.ndarray, close: np.ndarray, ha_close: np.ndarray):
    """
    Calculates heikin ashi open prices.

    Formula: (ha open[-1] + ha close[-1]) / 2

    :param open: open prices
    :param close: close prices
    :param ha_close: heikin ashi close prices
    :return: heikin ashi open prices
    """
    ha_open = np.empty(open.shape)
    ha_open[0] = (open[0] + close[0]) / 2

    for i in range(1, np.shape(open)[0]):
        ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2

    return ha_open


def to_heikin_ashi(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    """
    Calculates heikin ashi candlesticks.

    Calculation formula:
        - ha open: (ha open[-1] + ha close[-1]) / 2
        - ha high: max(high, ha open[0], ha close[0])
        - ha low: min(low, ha open[0], ha close[0])
        - ha close: (open[0], high[0], low[0], close[0]) / 4

    Note: [0] - means current, [-1] - means previous

    :param open: open prices
    :param high: high prices
    :param low: low prices
    :param close: close prices
    :return: tuple(ha open, ha high, ha low, ha close)
    """
    ha_close: np.ndarray = (open + high + low + close) / 4
    ha_open = heikin_ashi_open(open, close, ha_close)
    ha_high = np.maximum.reduce((high, ha_open, ha_close))
    ha_low = np.minimum.reduce((low, ha_open, ha_close))

    return ha_open, ha_high, ha_low, ha_close


def support(x: np.ndarray, /, n: int):
    """
    Returns a boolean numpy array.
    True where at least `n` consecutive value decreases before and increases after a value.

    :param x: 1d iterable
    :param n: lookback and lookahead period
    :return: boolean numpy array

    :examples:
    >>> arr = np.array([4, 3, 2, 1, 2, 3, 4])
    >>> support(arr, n=3)
    array([False, False, False,  True, False, False, False])

    >>> support(arr, n=2)
    array([False, False, False,  True, False, False, False])

    >>> arr2 = np.array([1, 2, 3, 4, 3, 2, 1])
    >>> support(arr2, n=2)
    array([False, False, False, False, False, False, False])
    """

    inc_arr = consecutive_increase(x, n)
    dec_arr = consecutive_decrease(x, n)

    dec_inc_arr = np.all(np.vstack((dec_arr[:-n], inc_arr[n:])), axis=0)
    return np.concatenate((dec_inc_arr, np.full(n, False)))


def resistance(x: np.ndarray, /, n: int):
    """
    Returns a boolean numpy array.
    True where at least `n` consecutive value increases before and decreases after a value.

    :param x: 1d iterable
    :param n: lookback and lookahead period
    :return: boolean numpy array

    :examples:
    >>> arr = np.array([4, 3, 2, 1, 2, 3, 4])
    >>> resistance(arr, n=3)
    array([False, False, False, False, False, False, False])

    >>> resistance(arr, n=2)
    array([False, False, False, False, False, False, False])

    >>> arr2 = np.array([1, 2, 3, 4, 3, 2, 1])
    >>> resistance(arr2, n=2)
    array([False, False, False,  True, False, False, False])
    """

    inc_arr = consecutive_increase(x, n)
    dec_arr = consecutive_decrease(x, n)

    dec_inc_arr = np.all(np.vstack((dec_arr[n:], inc_arr[:-n])), axis=0)
    return np.concatenate((dec_inc_arr, np.full(n, False)))
