from __future__ import annotations

import json
import logging
import os
import pathlib
import random
from functools import wraps
from typing import Callable, Iterable

import yaml


def singleton(callable_obj: Callable, /):
    """
    Decorator function.

    Calls wrapped callable only once and caches its value.
    :returns: Cached value returned by the wrapped function.
    """

    val = None

    def wrapper(*args, **kwargs):
        nonlocal val
        if val is None:
            val = callable_obj(*args, **kwargs)
        return val

    return wrapper


def read_json(*path):
    with open(os.path.join(*path)) as f:
        return json.loads(f.read())


def read_yaml(*path):
    with open(os.path.join(*path)) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def read_config(path: str) -> dict:
    """Reads a json or a yaml file."""
    extension = pathlib.Path(path).suffix
    if 'yaml' in extension:
        return read_yaml(path)
    if 'json' in extension:
        return read_json(path)


def round_down(number: float | int | None, precision: int):
    """
    Rounds down the `number` by a number of `precision` points (truncates value).

    :examples:
    >>> round_down(1, precision=2)
    1.0

    >>> round_down(1.1, precision=1)
    1.1

    >>> round_down(1.9999, precision=2)
    1.99
    """

    if number is None:
        return

    s = str(number)
    if '.' not in s:
        return float(number)

    return float(s[: s.find('.') + precision + 1])


def all_empty(values: Iterable):
    """
    Returns True if all `values` are 0, None or empty string.

    :examples:
    >>> all_empty(['0.0', '0', .0, None, ''])
    True

    >>> all_empty(['5', 'xy', '', None])
    False

    >>> all_empty([False, 'false', 'False'])
    False

    """

    for value in values:
        try:
            if value in ['', None]:
                continue
            elif float(value) != .0:
                return False
        except (ValueError, TypeError):
            return False

    return True


def all_zero(values: Iterable):
    """
    Returns True if all the `values` are 0.

    :examples:
    >>> all_zero(['0.0', '0', 0.0, 0])
    True

    >>> all_zero(['x', '0', None])
    False
    """

    for value in values:
        try:
            if float(value) != .0:
                return False
        except (ValueError, TypeError):
            return False
    return True


def all_none(values: Iterable):
    """
    Returns True if all the `values` are None.

    :examples:
    >>> all_none([1, 2, None])
    False

    >>> all_none([None, None, None])
    True
    """

    for value in values:
        if value is not None:
            return False
    return True


def remove_none(data: Iterable):
    """
    Removes all None values from `data`.

    :param data: Iterable
    :return: dict | list

    :examples:
    >>> remove_none([1, 2, None, 3, 4, None])
    [1, 2, 3, 4]
    """
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}

    return [x for x in data if x is not None]


def generate_character_sequence(start: int, end: int):
    return (chr(i) for i in range(start, end))


def generate_random_string(char_set: str, length: int):
    return ''.join(random.choice(char_set) for _ in range(length))


def get_object_from_module(module_name: str, object_name: str):
    import importlib

    module = importlib.import_module(module_name)

    return getattr(module, object_name)


class Immutable:
    """
    Makes object immutable. Disallows to set or delete attributes after __init__ gets called.
    """

    _immutable = False

    def __init__(self):
        self._immutable = True

    def __delattr__(self, key):
        if self._immutable:
            raise AttributeError(f'Not allowed to delete attribute {key}. This object is immutable!')
        object.__delattr__(self, key)

    def __setattr__(self, key, val):
        if self._immutable:
            raise AttributeError(f'Not allowed to set attribute {key}. This object is immutable!')
        object.__setattr__(self, key, val)


def immutable(cls):
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


def log_method_return(logger=logging.getLogger(), level=logging.INFO, log=True):
    """Class decorator function.

    Logs the return value of public functions.
    """
    def decorator(cls):

        def log_return(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                ret = func(self, *args, **kwargs)
                if ret is not None and log:
                    logger.log(level=level, msg=ret)
                return ret

            return wrapper

        for key, value in cls.__dict__.items():
            if not key.startswith('_') and isinstance(value, Callable):
                setattr(cls, key, log_return(value))

        return cls

    return decorator
