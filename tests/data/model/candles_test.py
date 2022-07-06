import numpy as np
import pytest

from trader.data.enumerate import OHLCV
from trader.data.model import Candles
from trader.data.schema import OPEN_TIME, VOLUME, CLOSE_PRICE, LOW_PRICE, HIGH_PRICE, OPEN_PRICE

tohlcv_candles = np.array([
    [1.0, 10.0, 15.0, 1.0, 5.0, 8.0],
    [2.0,  8.0,  5.0, 8.1, 1.2, 1.5],
    [3.0,  8.0,  9.0, 7.0, 8.0, 4.5],
    [4.0,  6.0, 10.2, 5.6, 7.0, 5.5],
])

c1 = Candles(
    candles=tohlcv_candles,
    symbol='XYZ',
    interval='1h',
    market='FUTURES',
    schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME),
)


def test_create_candles():

    # Invalid schema
    with pytest.raises(ValueError):
        Candles(
            candles=tohlcv_candles,
            symbol='',
            interval='',
            market='FUTURES',
            schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE),
        )

    # Invalid data
    with pytest.raises(ValueError):
        Candles(
            candles=np.ndarray([5, 10, 15]),
            symbol='',
            interval='',
            market='FUTURES',
            schema=(OPEN_TIME, OPEN_PRICE, HIGH_PRICE),
        )


def test_filter_candle_series():
    assert np.array_equal(c1.series(OPEN_TIME), [1., 2., 3., 4.])
    assert np.array_equal(c1.series(0), [1., 2., 3., 4.])
    assert np.array_equal(c1.series(OHLCV.OPEN_PRICE), [10., 8., 8., 6.])

    assert np.array_equal(
        c1.series([OPEN_PRICE, HIGH_PRICE, LOW_PRICE]),
        [
            [10., 8.,  8., 6.],
            [15., 5.,  9., 10.2],
            [1.,  8.1, 7., 5.6]
        ]
    )


def test_filter_candles_by_index():
    assert np.array_equal(
        c1[1:4].candles,
        np.array([
            [2.0, 8.0, 5.0, 8.1, 1.2, 1.5],
            [3.0, 8.0, 9.0, 7.0, 8.0, 4.5],
            [4.0, 6.0, 10.2, 5.6, 7.0, 5.5],
        ])
    )

    assert np.array_equal(
        c1[0::2].candles,
        [
            [1.0, 10.0, 15.0, 1.0, 5.0, 8.0],
            [3.0, 8.0, 9.0, 7.0, 8.0, 4.5],
        ]
    )


def test_candle_timeframe_filter():
    assert np.array_equal(
        c1.between(2, 3).candles,
        np.array([
            [2.0, 8.0, 5.0, 8.1, 1.2, 1.5],
            [3.0, 8.0, 9.0, 7.0, 8.0, 4.5],
        ])
    )

    assert np.array_equal(
        c1.between(0, 10).candles,
        np.array([
            [1.0, 10.0, 15.0, 1.0, 5.0, 8.0],
            [2.0, 8.0, 5.0, 8.1, 1.2, 1.5],
            [3.0, 8.0, 9.0, 7.0, 8.0, 4.5],
            [4.0, 6.0, 10.2, 5.6, 7.0, 5.5],
        ])
    )


def test_normalize_candles():
    data = np.array([
        [1, 1, 1, 1, 1, 1],
        [2, 2, 3, 2, 2, 2],
        [3, 3, 3, 3, 3, 3],
        [4, 4, 3, 4, 4, 4],
        [5, 5, 3, 5, 5, 5],
        [6, 6, 6, 6, 6, 6]
    ])

    candles = Candles(candles=data, symbol='SPY', interval='15m', market='FUTURES')

    norm_candles = candles.normalize(OPEN_PRICE, HIGH_PRICE)

    assert np.array_equal(norm_candles.open_prices, [0., 0.2, 0.4, 0.6, 0.8, 1.])
    assert np.array_equal(norm_candles.high_prices, [0., 0.4, 0.4, 0.4, 0.4, 1.])
    assert np.array_equal(norm_candles.times, [1, 2, 3, 4, 5, 6])
    assert np.array_equal(norm_candles.close_prices, [1, 2, 3, 4, 5, 6])

    print('\n', norm_candles, sep='')


def test_blend_candles():
    data = np.array([
        [1, 1, 1, 1, 1, 1],
        [2, 2, 3, 2, 2, 2],
        [3, 3, 3, 3, 3, 3],
        [4, 4, 3, 4, 4, 4],
        [5, 5, 3, 5, 5, 5],
        [6, 6, 6, 6, 6, 6]
    ])

    candles = Candles(candles=data, symbol='SPY', interval='15m', market='FUTURES')

    blended_candles = candles.blend()

    print(blended_candles)
