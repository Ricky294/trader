from typing import Union, Iterable

import numpy as np

from ..enum import OHLCV
from ..model import Candles


def map_match(src, tar):
    src_size = np.shape(src)[0]
    tar_size = np.shape(tar)[0]
    src_mat = src[:, np.newaxis]
    tar_mat = np.reshape(np.tile(tar, src_size), newshape=(src_size, tar_size))
    mask = np.sum(np.equal(src_mat, tar_mat), axis=-1)
    ret = src * mask
    return ret


def slope(arr: np.ndarray, period: int):
    sliding_arr = np.lib.stride_tricks.sliding_window_view(arr, period)
    sliding_arr = np.concatenate((sliding_arr[:, 0][:, None], sliding_arr[:, period-1][:, None]), axis=-1)

    nan_arr = np.full(period - 1, np.nan)
    slope_arr = (sliding_arr[:, 1] - sliding_arr[:, 0]) / period
    return np.concatenate((nan_arr, slope_arr))


def avg_line(candles: Candles, line: Union[Iterable, int, OHLCV]) -> np.ndarray:
    if isinstance(line, Iterable):
        return sum((candles.line(ln) for ln in line)) / len(candles)
    return candles.line(line)


def mask_match(src, tar):
    src_size = np.shape(src)[0]
    tar_size = np.shape(tar)[0]
    src_mat = src[:, np.newaxis]
    tar_mat = np.reshape(np.tile(tar, src_size), newshape=(src_size, tar_size))
    return np.any(np.equal(src_mat, tar_mat), axis=-1)


def fill_zeros_with_last(arr: np.ndarray):
    prev = np.arange(len(arr))
    prev[arr == 0] = 0
    prev = np.maximum.accumulate(prev)
    return arr[prev]


def assign_where_not_zero(arr, assign):
    arr_copy = np.copy(arr)
    arr_copy[arr_copy != 0.0] = assign

    return arr_copy
