import inspect
import logging
import os
from datetime import datetime
from functools import wraps

from util.inspect_util import is_public


def create_logger(
        name: str,
        *,
        fmt='%(levelname)s-%(name)s: %(message)s',
        date_fmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO,
        file_path: str = None,
):
    """
    Creates a new logger with a StreamHandler and a FileHandler if `file_path` is not None.

    If logger with `name` already exits returns existing logger.

    :param name: Logger name.
    :param fmt: Log message format.
    :param date_fmt: Log message date format.
    :param level: Minimum logging level.
    :param file_path: If not None, creates a file and logs messages to `file_path`.
    :return: Logger object
    """

    logger = logging.getLogger(name=name)
    if not logger.handlers:
        logger.propagate = False
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            fmt=fmt,
            datefmt=date_fmt,
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(level=level)

        stream_handler.setFormatter(fmt=formatter)
        logger.addHandler(stream_handler)

        if file_path is not None:
            if not os.path.exists(file_path):
                os.makedirs(file_path)

            create_time = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            file_handler = logging.FileHandler(filename=f'{file_path}/{create_time}.logs')
            file_handler.setLevel(level=logging.INFO)
            file_handler.setFormatter(fmt=formatter)
            logger.addHandler(file_handler)

    return logger


def log_return(logger: logging.Logger, *, level=logging.INFO, log=True, repr_=True):
    """
    Logs the return value of public methods.

    Can be applied on both functions and classes.
    """

    def wrapper(func_or_cls):

        def func_wrapper(func):
            @wraps(func)
            def args_wrapper(*args, **kwargs):
                ret = func(*args, **kwargs)
                if ret is not None and log:
                    logger.log(level=level, msg=f'{func.__qualname__} returned: {repr(ret) if repr_ else str(ret)}')
                return ret

            return args_wrapper

        def class_wrapper(cls):
            for key, value in vars(cls).items():
                if callable(value) and is_public(key):
                    setattr(cls, key, func_wrapper(value))
            return cls

        if inspect.isclass(func_or_cls):
            return class_wrapper(func_or_cls)
        else:
            return func_wrapper(func_or_cls)

    return wrapper


class LogReturnMeta(type):
    """
    Metaclass for logging return values.

    Logs the return value of every public methods.

    Propagates through inheritance.

    Check log_return decorator to see available parameters.
    """

    kwargs = {}

    def __new__(mcs, cls_name, cls_bases, cls_dict, **kwargs):
        cls_obj = super().__new__(mcs, cls_name, cls_bases, cls_dict)
        for key, val in kwargs.items():
            mcs.kwargs[key] = val
        cls_obj = log_return(**mcs.kwargs)(cls_obj)
        return cls_obj
