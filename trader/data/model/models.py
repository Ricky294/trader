from datetime import datetime
from typing import Any, TypeVar
import pandas as pd

from trader.data.model import Model

Model_T = TypeVar('Model_T', bound=Model)


class Models(list[Model_T]):

    @property
    def schema(self):
        try:
            return tuple(self[0].__dict__.keys())
        except IndexError:
            return tuple()

    def to_dict(self):
        return {
            key: tuple(obj.__dict__[key] for obj in self)
            for key in self.schema
        }

    def to_dataframe(self, *drop_columns: str, drop_na=True) -> pd.DataFrame:
        df = pd.DataFrame.from_records([obj.to_dict() for obj in self])
        df.drop(list(drop_columns), axis=1, inplace=True)
        if drop_na:
            df.dropna(axis=1, how='all', inplace=True)
        return df

    @property
    def id(self) -> list[Any]:
        return [obj.id for obj in self]

    @property
    def create_time(self) -> list[datetime]:
        return [obj.create_time for obj in self]

    @property
    def create_timestamp(self) -> list[float]:
        return [obj.create_timestamp for obj in self]
