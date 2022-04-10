"""This module provides common functions implemented in numpy."""

from __future__ import annotations

__all__ = (
    "to_numpy_array",
    "replace_where_not_found", "replace_where", "replace_with_previous_where",
    "local_max", "local_min",
    "increase", "consecutive_increase",
    "decrease", "consecutive_decrease",
    "shift",
)

from typing import Iterable

import numpy as np
import pandas as pd


def to_numpy_array(x, /, dtype: object | None = None,):
    """
    Converts parameter `x` to a numpy array.

    :return: numpy array

    :examples:
    >>> to_numpy_array(1)
    array([1])

    >>> to_numpy_array(1.5)
    array([1.5])

    >>> to_numpy_array([1, 2, 3])
    array([1, 2, 3])

    >>> to_numpy_array(np.array([1, 2, 3]))
    array([1, 2, 3])

    >>> to_numpy_array(pd.DataFrame({"x": [1, 3, 5], "y": [2, 4, 6]}), dtype=np.float32)
    array([[1., 2.],
           [3., 4.],
           [5., 6.]], dtype=float32)
    """
    if isinstance(x, np.ndarray):
        return x.copy()
    elif isinstance(x, pd.DataFrame):
        return x.to_numpy(dtype=dtype)
    elif isinstance(x, Iterable):
        return np.array(x, dtype=dtype)
    else:
        return np.array([x], dtype=dtype)


def replace_where_not_found(x1: np.ndarray, x2: np.ndarray, /, replace):
    """
    Replaces values with `replace` in `x1` where no equal element is present in `x2`.

    `x1` and `x2` can have different lengths.

    Note: Parameter assignment of `x1` and `x2` is not interchangeable.

    :param x1: 1D iterable
    :param x2: 1D iterable
    :param replace: Replacement value where condition is True.
    :return: numpy array

    :examples:
    >>> arr = np.array([5, 10, 11, 3, 1, 2])
    >>> replace_where_not_found(arr, np.array([5, 11, 2]), 0)
    array([ 5,  0, 11,  0,  0,  2])

    >>> replace_where_not_found(np.array([5, 11, 2]), arr, 0)
    array([ 5, 11,  2])

    >>> replace_where_not_found(arr, np.array([5, 5, 2, 2]), [1, 2, 3, 4])
    array([5, 1, 2, 3, 4, 2])
    """
    x1_copy = x1.copy()
    x2_copy = x2.copy()
    arr_matrix = x2_copy.reshape(x2_copy.size, 1)
    mask = np.all(x1_copy != arr_matrix, axis=0)

    return replace_where(x1_copy, mask, replace=replace)


def replace_where(x: np.ndarray, condition: np.ndarray, /, replace) -> np.ndarray:
    """
    Replaces values in `arr` where `condition` evaluates to True with `replace`.

    :param x: Numpy array in which elements get replaced based on condition.
    :param condition: Replacement condition.
    :param replace: Contains the replacement value(s).
    :return: numpy array
    :raises ValueError: replace must be constant or its length must equal with the condition mask True count.

    :examples:
    >>> arr = np.array([1, 2, 3, 4, 5])
    >>> replace_where(arr, arr > 3, 0)
    array([1, 2, 3, 0, 0])

    >>> replace_where(arr, arr > 3, [0, 1])
    array([1, 2, 3, 0, 1])

    >>> replace_where(arr, arr > 3, [0, 1, 2])
    ValueError: Cannot assign 3 input values to the 2 output values where the mask is true.
    """
    x_copy = x.copy()
    if isinstance(replace, Iterable):
        replace = to_numpy_array(replace)

    x_copy[condition] = replace
    return x_copy


def replace_with_previous_where(x: np.ndarray, condition: np.ndarray, /) -> np.ndarray:
    """
    Replaces values in `x` with its previous value where `condition` is True.

    :param x: 1D iterable
    :param condition: boolean 1D numpy array
    :return: numpy array

    :examples:
    >>> arr = np.array([1, 2, 3, 4, 5])
    >>> replace_with_previous_where(arr, arr > 2)
    array([1, 2, 2, 2, 2])

    >>> arr2 = np.array([1, 0, 0, 1, 0])
    >>> replace_with_previous_where(arr2, arr2 == 0)
    array([1, 1, 1, 1, 1])
    """
    x_copy = x.copy()
    prev = np.arange(len(x_copy))
    prev[condition] = 0
    prev = np.maximum.accumulate(prev)
    return x_copy[prev]


def local_min(x: np.ndarray, /, period: int):
    """
    Returns the minimum values on `x` with lookback `period` using a sliding window.

    :param x: 1D iterable
    :param period: lookback period
    :return: numpy array

    :examples:
    >>> local_min(np.array([1, 2, 3, 4, 2, 1, 5, 3]), period=3)
    array([nan, nan,  1.,  2.,  2.,  1.,  1.,  1.])
    """
    arr_window = np.lib.stride_tricks.sliding_window_view(x, period)
    minima_by_period = arr_window.min(axis=-1)
    nan_arr = np.full(period - 1, np.nan)
    return np.concatenate((nan_arr, minima_by_period))


def local_max(x: np.ndarray, /, period: int):
    """
    Returns the maximum values on `x` with lookback `period` using a sliding window.

    :param x: 1D iterable
    :param period: lookback period
    :return: numpy array

    :examples:
    >>> local_max(np.array([1, 2, 3, 4, 2, 1, 5, 3]), period=3)
    array([nan, nan,  3.,  4.,  4.,  4.,  5.,  5.])
    """
    arr_window = np.lib.stride_tricks.sliding_window_view(x, period)
    maxima_by_period = arr_window.max(axis=-1)
    nan_arr = np.full(period - 1, np.nan)
    return np.concatenate((nan_arr, maxima_by_period))


def decrease(x: np.ndarray, /):
    """
    Returns True where previous value is greater than next value.

    Similar method(s):
        - consecutive_decrease

    :param x: numpy array
    :return: boolean numpy array

    :examples:
    >>> decrease(np.array([1, 2, 3, 2, 1]))
    array([False, False, False,  True,  True])
    """
    return np.concatenate(([False], x[:-1] > x[1:]))


def increase(x: np.ndarray, /):
    """
    Returns True where previous value is less than next value.

    Similar method(s):
        - consecutive_increase

    :param x: numpy array
    :return: boolean numpy array

    :examples:
    >>> increase(np.array([1, 2, 3, 2, 1]))
    array([False,  True,  True, False, False])
    """
    return np.concatenate(([False], x[:-1] < x[1:]))


def consecutive_increase(x: np.ndarray, /, n: int):
    """
    Returns True where at least `n` previous value is less than current value.

    Similar method(s):
        - increase

    :param x: numpy array
    :param n: After at least this many consecutive increasing value returns True
    :return: boolean numpy array

    :examples:
    >>> consecutive_increase(np.array([1, 2, 3, 4, 3, 2, 1]), n=3)
    array([False, False, False,  True, False, False, False])
    """

    inc = increase(x)
    inc_window = np.lib.stride_tricks.sliding_window_view(inc, n)

    return np.concatenate((np.full(n - 1, False), np.all(inc_window, axis=-1)))


def consecutive_decrease(x: np.ndarray, /, n: int):
    """
    Returns True where at least `n` previous value is greater than current value.

    Similar method(s):
        - decrease

    :param x: numpy array
    :param n: After at least this many consecutive decreasing value returns True
    :return: boolean numpy array

    :examples:
    >>> consecutive_decrease(np.array([1, 2, 3, 4, 3, 2, 1]), n=3)
    array([False, False, False, False, False, False,  True])
    """

    inc = decrease(x)
    inc_window = np.lib.stride_tricks.sliding_window_view(inc, n)

    return np.concatenate((np.full(n - 1, False), np.all(inc_window, axis=-1)))


def shift(x: np.ndarray | Iterable | int | float, num: int, /, fill_value=np.nan, dtype=np.float):
    """
    Left or right shifts `x` by `num` and fills the shifter values with `fill_values`.

    :param x: Numpy array to shift.
    :param num: Left shifts (if less than 0) or right shifts (if greater than 0) x, this number of times.
    :param fill_value: Shifted values are replaced by this.
    :param dtype: Numpy data type
    :return: numpy array

    :examples:
    >>> x = [1, 2, 3, 4]
    >>> shift(x, 2)
    array([nan, nan,  1.,  2.])

    >>> shift(x, -2, fill_value=0)
    array([3., 4., 0., 0.])
    """

    result = np.empty_like(x, dtype=dtype)
    if num > 0:
        result[:num] = fill_value
        result[num:] = x[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = x[-num:]
    else:
        result[:] = x
    return result
