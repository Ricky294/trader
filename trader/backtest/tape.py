from typing import Callable

import numpy as np


class ArrayTape:

    def __init__(self, array: np.ndarray):
        self.__i = 0
        self.__len = array.shape[0]
        self.__array = array

    @classmethod
    def from_callback(cls, array: np.ndarray, callback: Callable[[np.ndarray], np.ndarray]):
        callback_array = callback(array)
        if callback_array.shape[0] == array.shape[0]:
            return cls(callback_array)
        else:
            raise ValueError("'callback' array shape differs from 'array'.")

    def __call__(self, data: np.ndarray):
        array_split = self.__array[:data.shape[0]]
        return array_split

    def __next__(self):
        if self.__i >= self.__len:
            raise StopIteration
        self.__i += 1
        next_split = self.__array[:self.__i]
        return next_split

    def __iter__(self):
        return self

    def __len__(self):
        return self.__len
