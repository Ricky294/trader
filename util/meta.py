"""
Module which contains function and class decorators and metaclasses.
"""
from functools import wraps
from typing import Callable


def func_wrapper(func: Callable, /):
    @wraps(func)
    def inner_func(*args, **kwargs):
        return func(*args, **kwargs)

    return inner_func


def singleton(func: Callable, /):
    """
    Decorator function.

    Calls wrapped callable only once and caches its value.
    :returns: Cached value returned by the wrapped function.
    """

    obj = None

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal obj
        if obj is None:
            obj = func(*args, **kwargs)
        return obj

    return wrapper


class ImmutableMeta(type):

    def __new__(mcs, name, bases, dct):
        dct['_frozen'] = False
        cls = super().__new__(mcs, name, bases, dct)

        def __setattr__(self, key, value):
            if self._frozen:
                raise AttributeError(f'Tried to reassign {key!r} on a frozen {cls.__name__!r} instance!')

            return object.__setattr__(self, key, value)

        cls.__setattr__ = __setattr__
        return cls


class Immutable:
    """
    Makes object immutable. Disallows to set or delete attributes after __init__ gets called.
    """

    _immutable = False

    def __init__(self):
        self._immutable = True

    def __setattr__(self, key, val):
        if self._immutable:
            raise AttributeError(f'Not allowed to set attribute {key}. This object is immutable!')
        object.__setattr__(self, key, val)

    def __delattr__(self, key):
        if self._immutable:
            raise AttributeError(f'Not allowed to delete attribute {key}. This object is immutable!')
        object.__delattr__(self, key)


def immutable(cls, /):
    """Class decorator function.

    Prevents setting attributes after __init__ was called.
    """

    def raise_attribute_error(obj: object, name: str, value: any):
        raise AttributeError(
            f'Not allowed to set {name}={value} because class {obj.__class__.__name__} is immutable.'
        )

    def init_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.__setattr__ = raise_attribute_error

        return wrapper

    cls.__init__ = init_decorator(cls.__init__)
    return cls
