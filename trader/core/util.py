from functools import wraps
from typing import Callable, Any, Iterable

from util.inspect_util import is_array_return_annotated_func, is_dunder
from util.iter_util import (
    get_array_return_annotated_func_names,
    get_iterable_attr_names,
    get_class_attrs,
)


arr_ret_func_names = '_arr_ret_func_names'
candles_name = '_candles'
ind_names = '_indicator_names'
iter_attr_names = '_iter_attr_names'


def sliced_iterable_getattribute_wrapper(getattr: Callable[[object, str], Any]):

    def get_sliced_iterable_attribute(self, attr_name: str):
        attr = getattr(self, attr_name)

        if attr_name in getattr(self, iter_attr_names):
            candles = getattr(self, candles_name)
            return attr[:len(candles)]
        elif attr_name in getattr(self, arr_ret_func_names):
            return lambda: attr()
        elif attr_name in getattr(self, ind_names):
            candles = getattr(self, candles_name)
            attr(candles)

        return attr

    return get_sliced_iterable_attribute


def cache_iterable_func_result(obj, func: Callable[[], Iterable]):
    cached_res = func()

    @wraps(func)
    def slice_func_result() -> Iterable:
        return cached_res[:len(obj._candles)]

    return slice_func_result


def get_indicator_names(attrs: dict[str, Any]):
    from trader.core.indicator.base import Indicator
    return [attr_name for attr_name, attr in attrs.items() if isinstance(attr, Indicator)]


def cache_array_return_annotated_funcs(obj):
    for attr_name, attr in get_class_attrs(obj).items():
        if is_array_return_annotated_func(attr):
            setattr(obj, attr_name, cache_iterable_func_result(obj, attr))


def store_iterable_object_names(obj):
    """
    Stores the following attribute names on `obj`:
        * iterable attribute names (e.g. list, tuple, numpy array)
        * iterable return annotated function names (e.g. list, tuple, numpy array)
        * indicator instance names
    """

    attrs = {
        attr_name: attr
        for attr_name, attr in get_class_attrs(obj).items()
        if not is_dunder(attr_name)
    }

    setattr(obj, ind_names, get_indicator_names(attrs))
    setattr(obj, iter_attr_names, get_iterable_attr_names(attrs, exclude=[arr_ret_func_names, ind_names, iter_attr_names]))
    setattr(obj, arr_ret_func_names, get_array_return_annotated_func_names(attrs))
