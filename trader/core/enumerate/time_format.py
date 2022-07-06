from enum import Enum


class TimeFormat(Enum):

    TIMESTAMP = 'ts'
    PANDAS = 'pd'
    DATETIME = 'dt'

    def __str__(self):
        return self.value
