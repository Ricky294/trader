from typing import Iterable, Mapping

import numpy as np


def remove_none(data: Iterable):
    """
    Removes all None values from `data`.

    :param data: Iterable
    :return: dict | np.ndarray | list | set | tuple ...

    :examples:
    >>> remove_none([0, 1, 2, None, 3, 4, None])
    [0, 1, 2, 3, 4]

    >>> remove_none((0, 1, 2, None, 3, 4, None))
    (0, 1, 2, 3, 4)

    >>> remove_none({0, 1, 2, None, 3, 4, None})
    {0, 1, 2, 3, 4}

    >>> remove_none(np.array([0, 1, 2, None, 3, 4, None]))
    array([0, 1, 2, 3, 4])

    >>> remove_none({'x': None, 'y': 15, 'z': 2})
    {'y': 15, 'z': 2}
    """

    if isinstance(data, Mapping):
        return {k: v for k, v in data.items() if v is not None}
    if isinstance(data, np.ndarray):
        return np.array([x for x in data if x is not None])

    return type(data)(x for x in data if x is not None)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
