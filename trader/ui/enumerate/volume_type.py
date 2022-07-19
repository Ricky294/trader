from enum import Enum


class Volume(Enum):
    LINE = 'Line'
    BAR = 'Bar'

    def __str__(self):
        return self.value
