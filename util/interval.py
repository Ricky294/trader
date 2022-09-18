__all__ = ['SEC_MAP', 'split_interval', 'interval_to_seconds', 'seconds_to_interval']

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

    value, timeframe = split_interval(str(interval))
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


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
