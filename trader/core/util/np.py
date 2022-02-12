from enum import Enum
from typing import Union

import numpy as np

from .common import compare


class Fit(Enum):
    FIRST = (0, (False, True))
    AFTER_LAST = (0, (True, False))
    ALL_BUT_FIRST = (0, (True, True))
    LAST = (-1, (True, False))
    BEFORE_FIRST = (-1, (False, True))


def cross_signal(
        arr: np.ndarray,
        logical_operator: str,
        other: Union[float, np.ndarray],
        fit_option: Fit,
) -> np.ndarray:
    other_is_array = isinstance(other, np.ndarray)
    if arr.size == 0 or (other_is_array and other.size == 0):
        raise ValueError("Array must not be empty!")

    if other_is_array:
        if arr.size > 1:
            other = np.lib.stride_tricks.sliding_window_view(other, (2,))
        first_value = compare(arr[0], logical_operator, other[0])
    else:
        first_value = compare(arr[0], logical_operator, other)

    if arr.size == 1:
        return np.array([first_value])

    sliding_array = np.lib.stride_tricks.sliding_window_view(arr, (2,))
    sliding_array_mask = compare(sliding_array, logical_operator, other)

    x = np.insert(sliding_array_mask == fit_option.value[1], fit_option.value[0], first_value, axis=0)
    return x.all(axis=-1)


def map_match(src, tar):
    src_size = np.shape(src)[0]
    tar_size = np.shape(tar)[0]
    src_mat = src[:, np.newaxis]
    tar_mat = np.reshape(np.tile(tar, src_size), newshape=(src_size, tar_size))
    mask = np.sum(np.equal(src_mat, tar_mat), axis=-1)
    ret = src * mask
    return ret


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
