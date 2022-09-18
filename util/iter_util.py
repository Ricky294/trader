import copy
import inspect
from abc import abstractmethod

from functools import wraps
from typing import Callable, Any, Collection, Sequence

import numpy as np

from util.inspect_util import is_public, is_iterable, is_array_return_annotated_func


def get_iterable_attr_names(attrs: dict[str, Any], exclude: list[str] | tuple[str]) -> list[str]:
    return [
        attr_name
        for attr_name, attr in attrs.items()
        if is_iterable(attr) and attr_name not in exclude
    ]


def get_array_return_annotated_func_names(attrs: dict[str, Any]) -> list[str]:
    return [
        attr_name
        for attr_name, attr in attrs.items()
        if is_array_return_annotated_func(attr)
    ]


def get_class_attrs(obj, /) -> dict[str, Any]:
    """
    Returns instance and class attributes of `obj` as dict.
    """

    return {
        attr_name: getattr(obj, attr_name)
        for attr_name in dir(obj)
    }


class SliceIterator:
    """Iterates on array from start to end while keeping all previous elements.

    :example:
    >>> for e in SliceIterator([1, 2, 3]):
    ...     e
    [1]
    [1, 2]
    [1, 2, 3]

    >>> for e in SliceIterator((1, 2, 3)):
    ...     e
    (1,)
    (1, 2)
    (1, 2, 3)
    """

    __slots__ = 'start_index', '_seq', '_seq_len', '_i'

    def __init__(self, _seq: Sequence, start_index=0):
        self._seq = _seq
        self._seq_len = len(self._seq)

        self.start_index = start_index
        self._i = start_index

    def __iter__(self):
        self._i = self.start_index
        return self

    def __next__(self):
        if self._seq_len > self._i:
            self._i += 1
            return self._seq[:self._i]
        else:
            raise StopIteration


class SuperIterator:

    @abstractmethod
    def __len__(self):
        ...

    def __getitem__(self, item):
        cpy = copy.deepcopy(self)

        for key, val in vars(self).items():
            if is_iterable(val):
                setattr(cpy, key, val.__getitem__(item))

        return cpy

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i < self.__len__():
            ret = self[self._i]
        else:
            raise StopIteration

        self._i += 1
        return ret

    def slice_iter(self):
        return SliceIterator(self)


class X(SuperIterator):

    def __len__(self):
        return 4

    def __init__(self):
        self.var1 = 5
        self.var2 = 'str'
        self.a = [5, 10, 15, 20]
        super().__init__()

"""
for x in X().slice_iter():
    print(x.a)
"""

def _fun_replayer(fun: Callable[[...], Collection], *args, **kwargs):
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


def replayer(cls_or_func):
    """
    Class and function decorator to replay array like returns from start to end.

    :raises StopIteration: After all elements replayed.

    Function decorator example
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

    Class decorator example
    ----

    >>> @replayer
    ... class XY:
    ...
    ...    def a(self) -> list:
    ...        return [5, 10, 15]
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


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
