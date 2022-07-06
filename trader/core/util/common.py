from __future__ import annotations

import json
import os
import pathlib
import random
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
