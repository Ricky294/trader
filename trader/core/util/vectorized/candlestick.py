"""
This module helps you to identify candlestick patterns on numpy arrays:
    - bullish_candles
    - bearish_candles
    - consecutive_bullish_candles
    - consecutive_bearish_candles
    - bullish_engulfing
    - bearish_engulfing
    - bullish_three_line_strike
    - bearish_three_line_strike
    - hammer
    - hanging_man
"""

import numpy as np
import nputils as npu


def bullish_candles(open: np.ndarray, close: np.ndarray) -> np.ndarray:
    """
    Returns True where `close` price is greater than `open` price.

    :param open: open prices
    :param close: close prices
    :return: bool numpy array
    """
    return close > open


def bearish_candles(open: np.ndarray, close: np.ndarray) -> np.ndarray:
    """
    Returns True where `close` price is less than `open` price.

    :param open: open prices
    :param close: close prices
    :return: bool numpy array
    """
    return close < open


def consecutive_bullish_candles(open: np.ndarray, close: np.ndarray, n: int):
    """
    Returns True where `close` price is greater than `open` price
    after at least `n` consecutive times.

    :param n: True, where at least n number of consecutive candles are bullish.
    :param open: open prices
    :param close: close prices
    :return: bool numpy array

    :examples:
    >>> open = np.array([1, 2, 3, 4, 5, 2])
    >>> close = np.array([2, 3, 4, 5, 4, 3])
    >>> consecutive_bullish_candles(open, close, n=3)
    array([False, False,  True,  True, False, False])
    """
    is_bullish = bullish_candles(open, close)
    bullish_win = np.lib.stride_tricks.sliding_window_view(is_bullish, n)

    return np.concatenate((np.full(n - 1, False), np.all(bullish_win, axis=-1)))


def consecutive_bearish_candles(open: np.ndarray, close: np.ndarray, n: int):
    """
    Returns True where `close` price is less than `open` price
    after at least `n` consecutive times.

    :param n: True, where at least n number of consecutive candles are bearish.
    :param open: open prices
    :param close: close prices
    :return: bool numpy array

    :examples:
    >>> open = np.array([2, 3, 4, 5, 4, 3])
    >>> close = np.array([1, 2, 3, 4, 5, 2])
    >>> consecutive_bearish_candles(open, close, n=3)
    array([False, False,  True,  True, False, False])
    """
    is_bullish = bearish_candles(open, close)
    bullish_win = np.lib.stride_tricks.sliding_window_view(is_bullish, n)

    return np.concatenate((np.full(n - 1, False), np.all(bullish_win, axis=-1)))


def bullish_engulfing(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    """
    Recognizes bullish engulfing patterns.

    Conditions:
        - A bearish candle is followed by a bullish candle.
        - The bullish candle has a higher high and a lower low than the bearish.
        - The bullish candle closes above the bearish candle's open.
        - The bullish candle opens at or lower than the previous candle's close.

    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: boolean numpy array

    :examples:
    >>> open = np.array([6, 4, 7, 9])
    >>> high = np.array([8, 9, 10, 11])
    >>> low = np.array([2, 1, 5, 7])
    >>> close = np.array([4, 7, 9, 8])
    >>> bullish_engulfing(open, high, low, close)
    array([False,  True, False, False])
    """

    prev_open = open[:-1]
    curr_open = open[1:]
    prev_high = high[:-1]
    curr_high = high[1:]
    prev_low = low[:-1]
    curr_low = low[1:]
    prev_close = close[:-1]
    curr_close = close[1:]

    return np.concatenate((
        [False],
        (prev_low > curr_low)
        & (prev_high < curr_high)
        & (prev_open < curr_close)
        & (prev_close >= curr_open)
    ))


def bearish_engulfing(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray):
    """
    Recognizes bearish engulfing patterns.

    Conditions:
        - A bullish candle is followed by a bearish candle.
        - The bearish candle has a higher high and a lower low than the bullish.
        - The bearish candle closes below the bullish candle's open.
        - The bearish candle opens at or higher than the bullish candle's close.

    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: boolean numpy array

    :examples:
    >>> open = np.array([6, 4, 7, 9])
    >>> high = np.array([8, 9, 10, 11])
    >>> low = np.array([2, 1, 5, 7])
    >>> close = np.array([4, 7, 9, 8])
    >>> bullish_engulfing(open, high, low, close)
    array([False,  True, False, False])
    """

    prev_open = open[:-1]
    curr_open = open[1:]
    prev_high = high[:-1]
    curr_high = high[1:]
    prev_low = low[:-1]
    curr_low = low[1:]
    prev_close = close[:-1]
    curr_close = close[1:]

    return np.concatenate((
        [False],
        (prev_low > curr_low)
        & (prev_high < curr_high)
        & (prev_open > curr_close)
        & (prev_close <= curr_open)
    ))


def bullish_n_line_strike(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, n=3):
    """
    True where n consecutive bearish candle makes lower lows
    followed by a candle that closes above the first candle's high.

    :param n: Minimum number of consecutive bearish candles (default: 3)
    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: bool numpy array
    """

    bearish_n = npu.shift(consecutive_bearish_candles(open, close, n=n), 1, fill_value=False)
    decreasing_lows = npu.decrease(low, n-1)
    close_gt_high_n_ago = np.concatenate((np.full(n, False), close[n:] > high[:-n]))

    stack = np.vstack((decreasing_lows, close_gt_high_n_ago, bearish_n))
    result = np.all(stack, axis=0)
    return result


def bearish_n_line_strike(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, n=3):
    """
    True where n consecutive bullish candle makes higher highs
    followed by a candle that closes below the first candle's low.

    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: bool numpy array
    """

    bullish_n = npu.shift(consecutive_bullish_candles(open, close, n=n), 1, fill_value=False)
    increasing_highs = npu.increase(high, n-1)
    increasing_highs = npu.shift(increasing_highs, 1, fill_value=False)
    bullish_candles(open, close)
    close_lt_low_n_ago = np.concatenate((np.full(n, False), close[n:] < low[:-n]))

    stack = np.vstack((increasing_highs, close_lt_low_n_ago, bullish_n))
    result = np.all(stack, axis=0)
    return result


def hammer(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, n=2.) -> np.ndarray:
    """
    Returns True where the lower wick is at least `n` times the height of the body.

    Indicates a potential price reversal to the upside.

    :param n: Lower wick body ratio (default=2).
    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: bool numpy array

    :examples:
    >>> open = np.array([5])
    >>> close = np.array([4])
    >>> low = np.array([1])
    >>> hammer(open, None, low, close)
    array([ True])
    """

    is_bullish = bullish_candles(open, close)
    return body_to_lower_wick_ratio(open, low, close, n) & is_bullish


def hanging_man(open: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray, n=2.) -> np.ndarray:
    """
    Returns True where the lower wick is at least `n` times the height of the body and previous candle is bullish.

    Signals short.

    :param n: Lower wick body ratio (default=2).
    :param open: open prices
    :param low: low prices
    :param high: high prices
    :param close: close prices
    :return: bool numpy array

    :examples:
    >>> open = np.array([5])
    >>> close = np.array([4])
    >>> low = np.array([1])
    >>> hammer(open, None, low, close)
    array([ True])
    """

    shifted_bullish_candles = npu.shift(bullish_candles(open, close), 1, fill_value=False)
    return body_to_lower_wick_ratio(open, low, close, n) & shifted_bullish_candles


def body_to_lower_wick_ratio(open: np.ndarray, low: np.ndarray, close: np.ndarray, n=2.) -> np.ndarray:
    body_size = abs(open - close)
    open_or_close = np.where(open < close, open, close)
    lower_wick_size = open_or_close - low

    return lower_wick_size / body_size >= n