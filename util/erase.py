from typing import Iterable


def remove_none(data: Iterable):
    """
    Removes all None values from `data`.

    :param data: Iterable
    :return: dict | list

    :examples:
    >>> remove_none([1, 2, None, 3, 4, None])
    [1, 2, 3, 4]

    >>> remove_none({'x': None, 'y': 15, 'z': 2})
    {'y': 15, 'z': 2}
    """

    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}

    return [x for x in data if x is not None]


