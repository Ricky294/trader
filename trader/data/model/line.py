from typing import Iterable, Callable


class Line:
    pass


class AttrLine(Line):

    def __init__(self, data: Iterable, start_index=0):
        self._data = data
        self._i = start_index

    def __getitem__(self, item):
        return self._data[:self._i + 1].__getitem__(item)

    def __str__(self):
        return self._data[:self._i + 1].__str__()


class FuncLine(Line):

    def __init__(self, func: Callable[[], Iterable], start_index=0):
        self._func = func
        self._data = func()
        self._i = start_index

    def __call__(self, *args, **kwargs):
        return self._data[:self._i + 1]

    def __str__(self):
        return self._func.__str__()
