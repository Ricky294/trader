import numpy as np
import pytest

from trader.data.model import Columnar
from trader.data.schema import SchemaError


def test_correct():
    columns = ["open", "high"]
    data = np.array([[5, 10, 15, 20, 25], [8, 10, 15, 20, 25]])

    Columnar(data, columns)


def test_iter():
    columns = ["open", "high"]
    data = np.array([[5, 10, 15, 20, 25], [8, 10, 15, 20, 25]])

    i = 0
    for col, line in Columnar(data, columns):
        if i == 0:
            assert col == 'open'
            assert np.array_equal(data[i], line)
        if i == 1:
            assert col == 'high'
            assert np.array_equal(data[i], line)
        i += 1


def test_wrong_number_of_columns():
    columns = ["open"]
    data = np.array([[5, 10, 15, 20, 25], [8, 10, 15, 20, 25]])

    with pytest.raises(SchemaError):
        Columnar(data, columns)


def test_wrong_data_shape():
    columns = ["open"]
    data = np.array([5, 10, 15, 20, 25, 8, 10, 15, 20, 25])

    with pytest.raises(SchemaError):
        Columnar(data, columns)
