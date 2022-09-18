import configparser
import json
import os
import pathlib
from typing import Iterable, Union, AnyStr

import yaml

from util.inspect_util import is_iterable


StrOrBytesPath = Union[str, bytes, os.PathLike[str], os.PathLike[bytes]]


def make_dirs(paths: StrOrBytesPath):
    if is_iterable(paths):
        os.makedirs(os.sep.join(paths), exist_ok=True)
    else:
        os.makedirs(paths, exist_ok=True)


def split_path(path: AnyStr) -> list[str]:
    """
    Splits path into its components.

    Usage examples:

    >>> split_path('dir1/dir2/file.ext')
    ['dir1', 'dir2', 'file.ext']

    >>> split_path(r'dir1\\dir2\\file.ext')
    ['dir1', 'dir2', 'file.ext']
    """

    return os.path.normpath(path).split(os.sep)


def read_json(*paths: StrOrBytesPath) -> dict[str, any]:
    """Reads a json file as a dict."""

    with open(os.path.join(*paths)) as f:
        return json.loads(f.read())


def read_yaml(*paths: StrOrBytesPath) -> dict | list:
    with open(os.path.join(*paths)) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def read_ini(*paths: StrOrBytesPath):
    config = configparser.ConfigParser()
    config.read(os.path.join(*paths))
    return config


def read_config(path: str) -> dict | list | configparser.ConfigParser:
    """
    Reads a config file.

    Supported extensions:
        * .yaml / .yml
        * .json
        * .ini

    :raises ValueError: If file extension is not supported.
    """

    extension = pathlib.Path(path).suffix

    if extension in ['.yaml', '.yml']:
        return read_yaml(path)
    elif extension == '.json':
        return read_json(path)
    elif extension == '.ini':
        return read_ini(path)
    else:
        raise ValueError(f'Unsupported file extension: {extension}.')


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
