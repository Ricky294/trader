"""
Module which contains function and class decorators and metaclasses.
"""
from functools import wraps
from typing import Callable, Any

from util.inspect_util import is_return_annotated, is_public
from util.iter_util import get_class_attrs


def set_object_attrs(func: Callable, **attrs):
    """
    Wrapper function. Set `attrs` of object returned by `func`.

    :param func: Function which returns an object with __dict__.
    :param attrs: Attributes for the object returned by func.
    """
    def wrapper(*func_args, **func_kwargs):
        obj = func(*func_args, **func_kwargs)

        for attr_name, attr_value in attrs.items():
            setattr(obj, attr_name, attr_value)

        return obj

    return wrapper


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

        def __setattr__(self, key: str, value: Any) -> None:
            if self._frozen:
                raise AttributeError(f'Tried to reassign {key!r} on a frozen {cls.__name__!r} instance!')

            return object.__setattr__(self, key, value)

        cls.__setattr__ = __setattr__
        return cls


class Immutable:
    """
    Makes object immutable.

    Disallows to set or delete attributes after __init__ was called.
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

    Disallows to set attributes after __init__ was called.
    """

    def raise_attribute_error(obj: object, name: str, value: Any):
        raise AttributeError(
            f'Not allowed to set {name}={value} because class {obj.__class__.__name__} is immutable.'
        )

    def init_decorator(init):
        @wraps(init)
        def wrapper(self, *args, **kwargs):
            init(self, *args, **kwargs)
            self.__setattr__ = raise_attribute_error

        return wrapper

    cls.__init__ = init_decorator(cls.__init__)
    return cls


def force_return_annotation_on_public_methods(obj):
    """
    Ensures that all public methods are return annotated.

    :raises AttributeError: If any public method is not return annotated.
    """

    for name, obj in vars(obj).items():
        if is_public(name) and callable(obj) and not is_return_annotated(obj):
            raise AttributeError(f'Annotate all public methods! Method called: {name!r} is not return annotated!')


class StaticMeta(type):
    """Static metaclass.

    Disallows instance creation for class.
    """

    @staticmethod
    def _static_class(cls):
        def wrapper(*args, **kwargs):
            raise TypeError(f'{cls.__qualname__!r} cannot be instantiated because it is a static class.')

        return wrapper

    def __new__(mcs, name, bases, dct):
        cls = super().__new__(mcs, name, bases, dct)
        cls.__new__ = mcs._static_class(cls)
        return cls


def double_wrap(func: Callable):
    """
    Allows decorators to be used with or without arguments

    Example:
     * @decorator(with, arguments, and=kwargs)
     * @decorator
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # actual decorated function
            return func(args[0])
        else:
            # decorator arguments
            return lambda real_func: func(real_func, *args, **kwargs)

    return wrapper


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
