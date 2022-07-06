from enum import Enum


class Broker(Enum):

    BINANCE = 'BINANCE'

    def __str__(self):
        return self.value
