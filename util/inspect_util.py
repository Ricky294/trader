import inspect
from typing import Iterable

import numpy as np


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


def is_public(attr_name: str, /):
    """
    Returns True if `name` does not start with underscore.

    :examples:
    >>> is_public('public')
    True

    >>> is_public('_protected')
    False

    >>> is_public('__private')
    False

    >>> is_public('__dunder__')
    False
    """

    return not attr_name.startswith('_')


def is_public_callable(obj, /):
    """
    Returns True if `obj` is public (name does not starts with underscore)
    and callable.

    :return: True or False
    :example:

    >>> is_public_callable(lambda: 1)
    True

    >>> def a(x): ...
    >>> is_public_callable(a)
    True

    >>> def _a(x): ...
    >>> is_public_callable(_a)
    False

    >>> is_public_callable(5)
    False
    """

    return callable(obj) and is_public(obj.__class__.__name__)


def is_private(attr_name: str, /):
    """
    Returns True if `name` start with underscore.

    :examples:
    >>> is_private('public')
    False

    >>> is_private('_private')
    True

    >>> is_private('__dunder__')
    False
    """

    return attr_name.startswith('_') and not attr_name.startswith('__')


def is_dunder(attr_name: str, /):
    """
    True if attr_name starts and ends with double underscore ('__')

    >>> is_dunder('init')
    False

    >>> is_dunder('__init')
    False

    >>> is_dunder('__init__')
    True
    """
    return attr_name.startswith('__') and attr_name.endswith('__')


def is_return_annotated(obj, /):
    """
    True if `obj` has a return annotation.

    >>> def xy(): pass
    >>> is_return_annotated(xy)
    False

    >>> def xy() -> int: pass
    >>> is_return_annotated(xy)
    True

    :param obj:
    :return:
    """
    return inspect.signature(obj).return_annotation is not inspect._empty


def is_bool(val: str):
    if val.lower() in ('true', 'false'):
        return True
    return False


def is_number(val):
    """

    Examples:
    --------

    >>> is_number('1')
    True

    >>> is_number('1.1')
    True

    >>> is_number('-1.1')
    True
    """

    try:
        float(val)
        return True
    except ValueError:
        return False


def is_int(val: str):
    """

    Examples:
    --------

    >>> is_int('xy')
    False

    >>> is_int('1')
    True

    >>> is_int('-1')
    True

    >>> is_int('1.1')
    False

    >>> is_int('-1.1')
    False
    """

    if is_number(val):
        return '.' not in val

    return False


def is_array_return_annotated_func(obj):
    """
    Returns true if `obj` is callable, and it's return annotation is array-like.

    :examples:
    >>> def a() -> list: return [5, 10, 15]
    >>> is_array_return_annotated_func(a)
    True

    >>> def b(): return [5, 10, 15]
    >>> is_array_return_annotated_func(b)
    False

    >>> def c() -> int: return 5
    >>> is_array_return_annotated_func(c)
    False
    """

    return (
            callable(obj)
            and inspect.signature(obj).return_annotation
            # Return annotation is 'str' if annotation is imported from __future__.
            # Otherwise, it's 'type'.
            in [list, tuple, np.ndarray, 'list', 'tuple', 'np.ndarray']
    )


def is_iterable(arg):
    """
    Returns True if arg is instance of typing.Iterable but not instance of str or bytes.

    :example:
    >>> is_iterable('xyz')
    False

    >>> is_iterable(b'xyz')
    False

    >>> is_iterable([1, 2, 3])
    True

    >>> is_iterable((1, 2, 3))
    True

    >>> is_iterable({1, 2, 3})
    True
    """

    return isinstance(arg, Iterable) and not isinstance(arg, (str, bytes))


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
