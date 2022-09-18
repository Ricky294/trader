from typing import Final

from util.super_enum import SuperEnum


class Market(SuperEnum):
    SPOT: Final = 'SPOT'
    FUTURES: Final = 'FUTURES'
