import json
import os
import pathlib

import yaml


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
