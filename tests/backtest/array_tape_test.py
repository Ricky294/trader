import numpy as np
import pytest

from trader.backtest import ArrayTape


array = np.array(
    [
        [1, 5],
        [2, 9],
        [3, 12],
        [4, 10],
        [5, 6],
    ]
)


def buy_sell_signal(data: np.ndarray):
    data_T = data.T

    return np.concatenate((
        [data_T[1] < 7],
        [data_T[1] > 9],
    )).T


def test_array_tape():
    tape = ArrayTape(buy_sell_signal(array))

    assert len(tape) == 5

    assert np.array_equal(next(tape), np.array([[True], [False]]))
    assert np.array_equal(next(tape), np.array([[True, False], [False, False]]))
    next(tape)
    next(tape)
    next(tape)

    with pytest.raises(StopIteration):
        assert next(tape)


def test_array_tape_iteration():
    tape = ArrayTape(buy_sell_signal(array))

    for curr in tape:
        print(curr)


def test_array_tape_from_callback():
    tape = ArrayTape.from_callback(array, buy_sell_signal)

    assert len(tape) == 5
    for curr in tape:
        print(curr)
