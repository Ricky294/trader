import inspect
from dataclasses import dataclass, field, asdict, astuple
from datetime import datetime

import numpy as np
import pandas as pd

from util.generate import generate_uuid4

from itertools import count

instance_counter = count(1)


@dataclass(frozen=True, order=True, kw_only=True)
class Model:
    __count: int = field(default_factory=lambda: next(instance_counter), init=False, repr=False)
    id: str = field(default_factory=generate_uuid4)
    create_time: datetime = field(default_factory=datetime.now)

    def copy_with(self, **kwargs):
        signature = inspect.signature(self.__init__)
        init_params = tuple(name for name, parameter in signature.parameters.items())

        new_params = dict(
            (name, kwargs[name]) if name in kwargs else (name, val)
            for name, val in vars(self).items() if name in init_params
        )

        return type(self)(**new_params)

    @property
    def create_timestamp(self):
        return self.create_time.timestamp()

    def to_tuple(self):
        return astuple(self)

    def to_dict(self):
        return asdict(self)

    def to_array(self):
        return np.array(self.to_tuple())

    def to_dataframe(self):
        return pd.DataFrame(self.to_dict(), index=[0])
