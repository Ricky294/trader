from typing import Final

from .super_enum import SuperEnum


class Market(SuperEnum):
    SPOT: Final = 'SPOT'
    FUTURES: Final = 'FUTURES'
