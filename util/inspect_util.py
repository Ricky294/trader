import inspect
from typing import Iterable

import numpy as np


def is_public(name: str, /):
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

    return not name.startswith('_')


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


def is_magic(obj):
    return obj.startswith('__') and obj.endswith('__')


def is_return_annotated(obj):
    return inspect.signature(obj).return_annotation is not inspect._empty


def is_array_return_annotated(obj):
    """
    Returns true if `obj` is callable, and it's return annotation is array.

    :example:
    >>> def a() -> list:
    ...    return [5, 10, 15]
    ...

    >>> def a2():
    ...    return [5, 10, 15]
    ...

    >>> is_array_return_annotated(a)
    True

    >>> is_array_return_annotated(a())
    False

    >>> is_array_return_annotated(None)
    False

    >>> is_array_return_annotated(a2)
    False

    """

    # Return annotation is string if annotation is imported from __future__.
    # Otherwise, it's a type object.
    return (
            callable(obj)
            and inspect.signature(obj).return_annotation
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

