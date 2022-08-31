from typing import Iterable


def is_all_empty(values: Iterable):
    """
    Returns True if all `values` are 0, None or empty string.

    :examples:
    >>> is_all_empty(['0.0', '0', .0, None, '', 'None'])
    True

    >>> is_all_empty(['5', 'xy', '', None])
    False

    >>> is_all_empty([False, 'false', 'False'])
    False

    """

    for value in values:
        try:
            if value in ['', None, 'None']:
                continue
            elif float(value) != .0:
                return False
        except (ValueError, TypeError):
            return False

    return True


def is_all_zero(values: Iterable):
    """
    Returns True if all the `values` are 0.

    :examples:
    >>> is_all_zero(['0.0', '0', 0.0, 0])
    True

    >>> is_all_zero(['x', '0', None])
    False
    """

    for value in values:
        try:
            if float(value) != .0:
                return False
        except (ValueError, TypeError):
            return False
    return True


def is_all_none(values: Iterable):
    """
    Returns True if all the `values` are None.

    :examples:
    >>> is_all_none([1, 2, None])
    False

    >>> is_all_none([None, None, None])
    True
    """

    for value in values:
        if value is not None:
            return False
    return True
