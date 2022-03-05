import json
import operator
import os
import pathlib
import re

import importlib
import inspect
from abc import ABCMeta

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

import random
from typing import Union

import yaml


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


def round_down(number: Union[float, int, None], precision: int):
    if number is None:
        return

    s = str(number)
    if "." not in s:
        return float(number)

    return float(s[: s.find(".") + precision + 1])


def remove_none(data):
    if isinstance(data, dict):
        return {k: v for k, v in data.items() if v is not None}

    return [x for x in data if x is not None]


def generate_ascii(start: int, end: int):
    return (chr(n) for n in range(start, end))


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
}


def compare(left_value, logical_operator, right_value):
    return logical_operators[logical_operator](left_value, right_value)


def interval_to_seconds(interval: str):

    time = int(interval[0:len(interval) - 1])
    metric = interval[-1]

    if metric.lower() == "s":
        return time
    elif metric == "m":
        return time * 60
    elif metric.lower() == "h":
        return time * 3600
    elif metric.lower() == "d":
        return time * 86400
    elif metric.lower() == "w":
        return time * 604800
    elif metric == "M":
        return time * 2629800
    elif metric.lower() == "y":
        return time * 31557600


def pickle_loader(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def save_object(obj, filename):
    with open(filename, 'ab ') as outp:  # Overwrites any existing file.
        pickle.dump(obj, outp, pickle.HIGHEST_PROTOCOL)


def split_by_capital(txt: str):
    return (c for c in re.split(r'([A-Z][a-z]*\d*)', txt) if c)


def space_by_capital(txt: str):
    return " ".join(split_by_capital(txt))


def get_concrete_class_init_params2(module_name: str, module_package: str = None):
    module = importlib.import_module(name=module_name, package=module_package)

    concrete_strategies = {
        name: value
        for name, value in module.__dict__.items()
        if isinstance(value, ABCMeta) and not inspect.isabstract(value)
    }
    concrete_strategy_init_params = {
        key: [
            get_parameter_info(param)
            for param in inspect.signature(value.__init__).parameters.values()
            if param.name not in ("self", "args", "kwargs")
        ]
        for key, value in concrete_strategies.items()
    }

    return concrete_strategy_init_params


def get_parameter_info(param: inspect.Parameter):
    annotation_split = str(param.annotation).split("'")
    if len(annotation_split) == 1:
        annotation = annotation_split[0]
    else:
        annotation = annotation_split[1]

    if annotation == "inspect._empty":
        annotation = "typing.Any"

    default = str(param.default)
    if default in ("None", "<class 'inspect._empty'>"):
        default = ''

    return tuple((annotation, default))
