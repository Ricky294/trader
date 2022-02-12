import numpy as np
import pytest

from trader.core.util.np import cross_signal, Fit


def test_nan_cross_signal():
    arr = np.array([np.nan, np.nan, np.nan, 20])
    signal = cross_signal(arr, "<", 15, Fit.FIRST)
    expected = np.array([False, False, False, False])
    assert np.array_equal(expected, signal)

    arr2 = np.array([np.nan, np.nan, np.nan, 10])
    signal = cross_signal(arr2, "<", 15, Fit.FIRST)
    expected = np.array([False, False, False, True])
    assert np.array_equal(expected, signal)


def test_cross_signal_raises_exception():
    with pytest.raises(ValueError):
        assert cross_signal(np.array([]), ">", 15, Fit.FIRST)

    with pytest.raises(ValueError):
        assert cross_signal(np.array([]), ">", np.array([]), Fit.FIRST)


def test_size_1_cross_signal():
    arr = np.array([1])
    signal = cross_signal(arr, ">", 15, Fit.FIRST)
    expected = np.array([False])
    assert np.array_equal(expected, signal)

    arr = np.array([1])
    signal = cross_signal(arr, "<", 15, Fit.FIRST)
    expected = np.array([True])
    assert np.array_equal(expected, signal)


def test_size_2_cross_signal():
    arr = np.array([1, 20])
    signal = cross_signal(arr, ">", 15, Fit.FIRST)
    expected = np.array([False, True])
    assert np.array_equal(expected, signal)


def test_const_cross_signal():
    arr = np.array([10, 15, 20, 25, 8, 14, 16, 18])
    signal = cross_signal(arr, ">", 15, Fit.FIRST)

    expected = np.array([False, False, True, False, False, False, True, False])

    assert np.array_equal(expected, signal)


def test_array_1_cross_signal():
    arr = np.array([5])
    arr2 = np.array([1])

    signal = cross_signal(arr, "<", arr2, Fit.FIRST)
    expected = np.array([False])

    assert np.array_equal(expected, signal)


a = np.array([2, 1, 2, 3, 4, 5, 6, 6, 7])
b = np.array([1, 2, 3, 4, 5, 1, 2, 7, 8])
#             >, <, <, <, <, >, >, <, <


def test_array_cross_signal():
    signal = cross_signal(a, "<", b, Fit.FIRST)
    expected = np.array([False, True, False, False, False, False, False, True, False])

    assert np.array_equal(expected, signal)


def test_fit_last():
    signal = cross_signal(a, "<", b, Fit.LAST)

    expected = np.array([False, False, False, False, True, False, False, False, False])

    assert np.array_equal(expected, signal)


def test_fit_before_first():
    signal = cross_signal(a, "<", b, Fit.BEFORE_FIRST)

    expected = np.array([True, False, False, False, False, False, True, False, False])

    assert np.array_equal(expected, signal)


def test_fit_after_last():
    signal = cross_signal(a, "<", b, Fit.AFTER_LAST)

    expected = np.array([False, False, False, False, False, True, False, False, False])

    assert np.array_equal(expected, signal)


def test_fit_all_but_first():
    signal = cross_signal(a, "<", b, Fit.ALL_BUT_FIRST)

    expected = np.array([False, False, True, True, True, False, False, False, True])

    assert np.array_equal(expected, signal)

