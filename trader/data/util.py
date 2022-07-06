from __future__ import annotations

import numpy as np
import nputils as npu

SEC_MAP = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800,
    'M': 2629800,
    'Y': 31557600,
}


def split_interval(interval: str, /):
    """
    Decomposes interval to time value and time unit.

    :return: tuple - time value (int), time unit (str)

    :examples:
    >>> split_interval('15m')
    (15, 'm')

    >>> split_interval('1h')
    (1, 'h')

    >>> split_interval('200d')
    (200, 'd')
    """

    timeframe = interval[len(interval) - 1]
    value = interval[0: len(interval) - 1]

    return int(value), timeframe


def interval_to_seconds(interval: str, /) -> int:
    """
    Converts interval (str) to seconds (int)

    :examples:

    >>> interval_to_seconds('1m')
    60

    >>> interval_to_seconds('15m')
    900

    >>> interval_to_seconds('1h')
    3600

    >>> interval_to_seconds('2h')
    7200
    """

    value, timeframe = split_interval(interval)
    return value * SEC_MAP[timeframe]


def seconds_to_interval(seconds: int, /):
    """
    Converts seconds to interval (see examples).

    :examples:
    >>> seconds_to_interval(30)
    '30s'

    >>> seconds_to_interval(60)
    '1m'

    >>> seconds_to_interval(185)
    '3m 5s'

    >>> seconds_to_interval(192600)
    '2d 5h 30m'
    """

    def generate_intervals():
        nonlocal seconds
        for unit, in_seconds in reversed(list(SEC_MAP.items())):
            ratio = int(seconds / in_seconds)
            if ratio >= 1:
                yield f'{ratio}{unit}'
                seconds -= in_seconds * ratio

    return ' '.join(generate_intervals())


def check_ndim_is_2(data: np.ndarray):
    """
    Raises ValueError if numpy array's number of dimension is not 2.
    """

    if data.ndim != 2:
        raise ValueError(f'Candles dimension must be 2, not {data.ndim}.')


def blend_ohlc(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, period=2):
    """
    Candlestick blending, also known as candlestick math.

    Adds candlesticks together.

    Calculation formula:
        - open = The first open price in window.
        - high = The highest high price in window.
        - low = The lowest low price in window.
        - close = The last close price in window.

    :param period: Determines the size of the sliding window (default=2).
    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: blended open, high, low, close prices
    """

    ret_low = npu.min_over_period(low, period=period)
    ret_high = npu.max_over_period(high, period=period)

    open_window = np.lib.stride_tricks.sliding_window_view(open, period)
    close_window = np.lib.stride_tricks.sliding_window_view(close, period)

    ret_open = open_window[:, 0]
    ret_close = close_window[:, -1]

    ret_open = np.concatenate((
        np.full(period - 1, fill_value=ret_open[0]),
        ret_open,
    ))

    ret_close = np.concatenate((
        [i for i in ret_close[0: period - 1]],
        ret_close,
    ))

    return ret_open, ret_high, ret_low, ret_close


def heikin_ashi_open(open: np.ndarray, close: np.ndarray, ha_close: np.ndarray):
    """
    Calculates heikin ashi open prices.

    Formula: (ha open[-1] + ha close[-1]) / 2

    :param open: open prices
    :param close: close prices
    :param ha_close: heikin ashi close prices
    :return: heikin ashi open prices
    """
    ha_open = np.empty(open.shape)
    ha_open[0] = (open[0] + close[0]) / 2

    for i in range(1, np.shape(open)[0]):
        ha_open[i] = (ha_open[i-1] + ha_close[i-1]) / 2

    return ha_open


def to_heikin_ashi(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    """
    Calculates heikin ashi candlesticks.

    Calculation formula:
        - ha open: (ha open[-1] + ha close[-1]) / 2
        - ha high: max(high, ha open[0], ha close[0])
        - ha low: min(low, ha open[0], ha close[0])
        - ha close: (open[0], high[0], low[0], close[0]) / 4

    Note: [0] - means current, [-1] - means previous

    :param open: open prices
    :param high: high prices
    :param low: low prices
    :param close: close prices
    :return: tuple(ha open, ha high, ha low, ha close)
    """
    ha_close: np.ndarray = (open + high + low + close) / 4
    ha_open = heikin_ashi_open(open, close, ha_close)
    ha_high = np.maximum.reduce((high, ha_open, ha_close))
    ha_low = np.minimum.reduce((low, ha_open, ha_close))

    return ha_open, ha_high, ha_low, ha_close

