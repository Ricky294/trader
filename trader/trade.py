from __future__ import annotations

import numpy as np
import talib

from trader.core.const import MA


def talib_ma(data: np.ndarray, /, type: MA, period: int) -> np.ndarray:
    """
    Calculates moving average of `type` on `data` with lookback `period` using TA-Lib.
    """
    return getattr(talib, str(type))(data, timeperiod=period)


def cross(data: np.ndarray, /):
    """
    This function can be used to generate cross signals.

    :param data: boolean numpy array
    :return: boolean numpy array
    :examples:

    >>> cross(np.array([-2, -1, 1, 2, 3]) > 0)
    array([False, False, True, False, False])

    >>> cross(np.array([np.nan, np.nan, 1, -1, 1, 2]) > 0)
    array([False, False, False, False, True, False])

    >>> cross(np.array([1, 2, 3, 4, 5, 6]) <= np.array([0, 2, 4, 1, 2, 8]))
    array([False, True, False, False, False, True])
    """

    mask = np.where(data, True, False)
    sliding_arr = np.lib.stride_tricks.sliding_window_view(mask, 2)
    cross_signal = (sliding_arr[:, 0] == False) & (sliding_arr[:, 1] == True)

    ret = np.insert(cross_signal, 0, False)
    return ret


def slope(data: np.ndarray, /, period: int):
    """
    Calculates the slope on `data` on a `period` sliding window.

    Calculation formula (applied on every window):
        slope = (data[-1] - data[0]) / period

    :param data: 1D iterable
    :param period: Calculates the slope on every n period.
    :return: numpy array

    :examples:
    >>> slope(np.array([1, 2, 4, 8, 16, 32, 64, 128]), period=3)
    array([nan, nan,  1.,  2.,  4.,  8., 16., 32.])
    """

    sliding_arr = np.lib.stride_tricks.sliding_window_view(data, period)
    slope_arr = (sliding_arr[:, period - 1] - sliding_arr[:, 0]) / period

    return np.concatenate((np.full(period - 1, np.nan), slope_arr))
