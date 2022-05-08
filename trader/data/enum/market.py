from __future__ import annotations

from enum import Enum


class Market(Enum):

    SPOT = "SPOT"
    FUTURES = "FUTURES"

    def __str__(self):
        return self.value

    def __int__(self):
        return 0 if self.value == "SPOT" else 1
