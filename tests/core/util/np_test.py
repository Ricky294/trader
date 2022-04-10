import numpy as np

from trader.core.util.vectorized import to_numpy_array, replace_where, replace_where_not_found, replace_with_previous_where, \
    slope


def test_to_numpy_array():
    assert np.array_equal(np.array([1]), to_numpy_array(1))
    assert np.array_equal(np.array([1.1]), to_numpy_array(1.1))
    assert np.array_equal(np.array([1, 2]), to_numpy_array([1, 2]))
    assert np.array_equal(np.array([1, 2]), to_numpy_array(np.array([1, 2])))


def test_replace_where():
    arr = np.array([1, 2, 3, 4, 5])

    assert np.array_equal(replace_where(arr, arr > 3, replace=0), [1, 2, 3, 0, 0])
    assert np.array_equal(replace_where(arr, arr > 3, replace=[0, 1]), [1, 2, 3, 0, 1])
    assert np.array_equal(replace_where(arr, arr > 3, replace=np.array([0, 1])), [1, 2, 3, 0, 1])


def test_replace_matching():
    arr = np.array([5, 10, 11, 3, 1, 2])

    assert np.array_equal(replace_where_not_found(arr, [5, 11, 2], 0), [5, 0, 11, 0, 0, 2])
    assert np.array_equal(replace_where_not_found([5, 11, 2], arr, 0), [5, 11, 2])
    assert np.array_equal(replace_where_not_found(arr, [5, 5, 2, 2], 0), [5, 0, 0, 0, 0, 2])
    assert np.array_equal(replace_where_not_found(arr, [5, 5, 2, 2], [1, 2, 3, 4]), [5, 1, 2, 3, 4, 2])


def test_replace_with_previous_where():
    arr = np.array([1, 2, 3, 4, 5])
    assert np.array_equal(replace_with_previous_where(arr, arr > 2), [1, 2, 2, 2, 2])

    arr2 = np.array([1, 0, 0, 1, 0])
    assert np.array_equal(replace_with_previous_where(arr2, arr2 == 0), [1, 1, 1, 1, 1])

    arr3 = np.array([1, 3, 4, 2, 0])
    assert np.array_equal(replace_with_previous_where(arr3, arr3 >= arr), [1, 1, 1, 2, 0])


def test_slope():
    x = slope([1, 2, 4, 8, 16, 32], period=4)

    pass
