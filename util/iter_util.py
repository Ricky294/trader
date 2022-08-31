import inspect
from functools import wraps
from typing import Iterator, Callable

import numpy as np

from util.inspect_util import is_public, is_iterable, is_array_return_annotated


def public_attributes(obj):
    return filter(lambda x: not x.startswith('_'), dir(obj))


class ArraySliceWrapper:

    __slots__ = '_arr', 'i'

    def __init__(self, arr, /):
        self._arr = arr
        self.i = 1

    def update(self, obj):
        self.i = len(obj)

    def func_get(self, i, /):
        return lambda *args, **kwargs: self.get(i)


class ObjectSliceWrapper:

    __slots__ = ('obj', 'i')

    def __init__(self, obj, /):
        self.obj = obj
        self.i = 1

    def update(self, obj):
        self.i = len(obj)

    def __getattr__(self, name):
        obj = object.__getattribute__(self, 'obj')
        attr = obj.__getattribute__(name)
        if is_iterable(attr):
            return attr[:self.i]
        elif is_array_return_annotated(attr):
            return lambda *args, **kwargs: attr(*args, **kwargs)[:self.i]
        return attr


class ArraySliceIter(Iterator):
    """Iterates on array from start to end while keeping all previous elements.

    :example:
    >>> for e in ArraySliceIter([1, 2, 3]):
    ...     e
    [1]
    [1, 2]
    [1, 2, 3]

    >>> for e in ArraySliceIter((1, 2, 3)):
    ...     e
    (1,)
    (1, 2)
    (1, 2, 3)
    """

    __slots__ = ('_arr', '_i', '_len')

    def __init__(self, arr, /):
        self._len = len(arr)
        self._arr = arr
        self._i = 0

    @property
    def i(self):
        """Current index."""
        return self._i

    def __len__(self):
        return self._len

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= self._len:
            raise StopIteration

        self._i += 1
        return self._arr[:self._i]


def _fun_replayer(fun: Callable, *args, **kwargs):
    i = 0
    res = fun(*args, **kwargs)
    len_ = len(res)

    @wraps(fun)
    def wrapper():
        nonlocal i
        i += 1
        if len_ >= i:
            return res[:i]
        raise StopIteration
    return wrapper


def _cls_replayer(cls):

    def wrapper():
        for key, value in vars(cls).items():
            if (
                callable(value)
                and is_public(key)
                and inspect.signature(value).return_annotation in [list, tuple, np.ndarray]
            ):
                setattr(cls, key, _fun_replayer(value, cls))
        return cls
    return wrapper


def replayer(cls_or_func: Callable):
    """
    Class and function decorator to replay array like returns from start to end.

    :raises StopIteration: After all elements replayed.

    :example:

    Example - Function decorator
    ----

    >>> @replayer
    ... def xy():
    ...     return [1, 2, 3]
    ...
    >>> xy()
    [1]
    >>> xy()
    [1, 2]
    >>> xy()
    [1, 2, 3]
    >>> xy()
    Traceback (most recent call last):
    ...
    StopIteration

    Example - Class decorator
    ----

    >>> @replayer
    ... class XY:
    ...
    ...    def a(self) -> list:
    ...        return [5,10,15]
    ...
    >>> xy = XY()
    >>> xy.a()
    [5]
    >>> xy.a()
    [5, 10]
    >>> xy.a()
    [5, 10, 15]
    >>> xy.a()
    Traceback (most recent call last):
    ...
    StopIteration
    """

    if inspect.isclass(cls_or_func):
        return _cls_replayer(cls_or_func)
    else:
        return _fun_replayer(cls_or_func)
