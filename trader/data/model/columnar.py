from typing import Iterable, Literal

import numpy as np
import pandas as pd

from trader.config import (
    BALANCE_PRECISION,
    FEE_PRECISION,
    MONEY_PRECISION,
    PRICE_PRECISION,
    PROFIT_PRECISION,
    QUANTITY_PRECISION,
)
from trader.core.util.common import all_empty
import trader.core.util.format as fmt


class Columnar:
    """
    Useful super_enum.py class to store 2D data structure in columnar orientation.
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


def format_trade(
        columnar: Columnar,
        unit: Literal['D', 's', 'ms', 'us', 'ns'],
        utc=False,
        exclude_empty=True,
):
    def format_values(name: str, values: Iterable):
        if 'time' in name:
            return [pd.to_datetime(value, unit=unit, utc=utc) for value in values]
        elif 'side' in name:
            return [str(value) for value in values]
        elif 'balance' in name:
            prec = BALANCE_PRECISION
        elif 'fee' in name:
            prec = FEE_PRECISION
        elif 'amount' in name:
            prec = MONEY_PRECISION
        elif 'price' in name:
            prec = PRICE_PRECISION
        elif 'profit' in name:
            prec = PROFIT_PRECISION
        elif 'quantity' in name:
            prec = QUANTITY_PRECISION
        else:
            prec = -1

        if prec == -1:
            return [str(value) for value in values]
        return fmt.num(values, prec=prec)

    fmt_dict = {col: format_values(col, values) for col, values in columnar.to_dict().items()}

    return (
        {col: data for col, data in fmt_dict.items() if not all_empty(data)}
        if exclude_empty
        else fmt_dict
    )
