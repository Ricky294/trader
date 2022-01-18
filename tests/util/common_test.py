import math

from trader.core.util.common import round_down, remove_none


def test_round_down():
    assert round_down(math.pi, 2) == 3.14
    assert round_down(math.pi, 4) == 3.1415
    assert round_down(3, 0) == 3
    assert round_down(3, 10) == 3
    assert round_down(21415471.14, 5) == 21415471.14
    assert round_down(None, 5) is None


def test_remove_none():
    dct1 = {"key1": 15, "key2": "val1", 55: 31.484}
    assert remove_none(dct1) == dct1

    dct2 = {"key1": None, "key2": "val1", 55: None}
    assert remove_none(dct2) == {"key2": "val1"}
