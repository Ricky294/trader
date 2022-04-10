from enum import Enum


class Volume(Enum):
    LINE = 0
    BAR = 1
    NONE = 2

    def __str__(self):
        return self.value
