import numpy as np

from trader.core.indicator import IndicatorResult


def test_result():
    result = IndicatorResult(buy_signal=np.array([0, 1, 0]), sell_signal=np.array([1, 0, 1]))

    assert 1 == result.latest_sell_signal()
    assert 0 == result.latest_buy_signal()

    array = result.to_np_array()
    df = result.to_pd_dataframe()
