import copy
from uuid import uuid4
import time

import numpy as np
import pandas as pd


class Model:

    def __init__(self, _id: any, create_time: int | float | None):
        """
        Creates a value object.

        :param _id: Unique id for the object. Auto generated if not defined (Optional).
        :param create_time: Creation time in seconds. Gets current timestamp if not defined (Optional).
        """
        self.id = str(uuid4()) if _id is None else id
        self.time = time.time() if create_time is None else create_time

    def copy_init(self, **kwargs):
        """
        Creates a new object of type self.

        If there is a corresponding keyword argument in self,
        it uses the argument in the new object otherwise it copies the original value from self.

        :return: new object of type self
        """
        params = {
            key: kwargs[key] if key in kwargs
            else copy.deepcopy(val)
            for key, val in self.__dict__.items()
        }

        return type(self)(**params)

    def __str__(self):
        return (
            f'{self.__class__.__name__}(' +
            ', '.join(
                f'{key.strip("_")}={val}'
                for key, val in self.__dict__.items()
            ) + ')'
        )

    def __repr__(self):
        return (
            f'{self.__class__.__name__}(' +
            ', '.join(
                f'{key.strip("_")}={val!r}'
                for key, val in self.__dict__.items()
            ) + ')'
        )

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.id)

    def to_dict(self) -> dict[str, any]:
        return self.__dict__

    def to_list(self):
        return list(val for val in self.__dict__.values())

    def to_tuple(self):
        return tuple(val for val in self.__dict__.values())

    def to_array(self):
        return np.array([val for val in self.__dict__.values()])

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict(), index=[0])
