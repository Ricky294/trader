import numpy as np
import pandas as pd

from trader.core.enumerate import SideFormat, TimeFormat
from trader.core.enumerate.precision_format import PrecisionFormat
from trader.core.util.common import all_empty
from trader.core.util.trade import format_time, format_side, format_number


class Columnar:
    """
    Useful base class to store 2D data structure in columnar orientation.
    """

    def __init__(self):
        self.__i = 0

    def __len__(self):
        return len(self.data)

    @property
    def columns(self):
        return [key for key in self.__dict__.keys() if key[0] != '_']

    @property
    def data(self):
        return np.array([value for key, value in self.__dict__.items() if key[0] != '_'])

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items() if key[0] != '_'}

    def __iter__(self):
        self.__i = 0
        return self

    def __next__(self):
        if self.__i >= self.data.shape[0]:
            raise StopIteration

        col = self.columns[self.__i]
        data = self.data[self.__i]
        self.__i += 1
        return col, data

    def __getitem__(self, index: int | slice):
        if isinstance(index, slice):
            return self.data[index.start:index.stop:index.step]

        return self.data[index]

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict())


def format_columnar(columnar: Columnar, format_options: dict[str, any], exclude_empty=True):

    def fmt(col, array):
        format_obj = format_options[col]

        if isinstance(format_obj, TimeFormat):
            return format_time(array, format_obj)
        elif isinstance(format_obj, SideFormat):
            return format_side(array, format_obj)
        elif isinstance(format_obj, PrecisionFormat):
            return format_number(array, format_obj)
        return array

    fmt_dict = {
       col: fmt(col, array) if col in format_options
       else array
       for col, array in columnar.to_dict().items()
    }

    return (
        {col: data for col, data in fmt_dict.items() if not all_empty(data)}
        if exclude_empty
        else fmt_dict
    )


def format_trade(
        columnar: Columnar,
        time_format=TimeFormat.PANDAS,
        side_format=SideFormat.LONG_SHORT,
        exclude_empty=True,
):
    def get_format(col):
        if 'time' in col:
            return time_format
        elif 'side' in col:
            return side_format
        elif 'balance' in col:
            return PrecisionFormat.BALANCE
        elif 'fee' in col:
            return PrecisionFormat.FEE
        elif 'money' in col:
            return PrecisionFormat.MONEY
        elif 'price' in col:
            return PrecisionFormat.PRICE
        elif 'profit' in col:
            return PrecisionFormat.PROFIT
        elif 'quantity' in col:
            return PrecisionFormat.QUANTITY

    format_options = {col: get_format(col) for col in columnar.columns}

    return format_columnar(columnar, format_options=format_options, exclude_empty=exclude_empty)
