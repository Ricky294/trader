import importlib


def get_object(module_name: str, object_name: str):
    module = importlib.import_module(module_name)

    return getattr(module, object_name)
