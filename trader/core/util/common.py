from __future__ import annotations

import json
import operator
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
    extension = pathlib.Path(path).suffix
    if "yaml" in extension:
        return read_yaml(path)
    if "json" in extension:
        return read_json(path)


def round_down(number: float | int | None, precision: int):
    if number is None:
        return

    s = str(number)
    if "." not in s:
        return float(number)

    return float(s[: s.find(".") + precision + 1])


def remove_none(data: Iterable):
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}

    return [x for x in data if x is not None]


def generate_character_sequence(start: int, end: int):
    return (chr(i) for i in range(start, end))


def generate_random_string(chars: str, size: int):
    return "".join(random.choice(chars) for _ in range(size))


def get_object_from_module(module_name: str, object_name: str):
    import importlib

    module = importlib.import_module(module_name)

    return getattr(module, object_name)


logical_operators = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    "gt": operator.gt,
    "lt": operator.lt,
    "ge": operator.ge,
    "le": operator.le,
    "eq": operator.eq,
    "ne": operator.ne,
}


def compare(left_value, logical_operator: str | Callable[[any, any], any], right_value, /):
    if isinstance(logical_operator, str):
        return logical_operators[logical_operator](left_value, right_value)
    return logical_operator(left_value, right_value)
