from typing import Final

from util.super_enum import SuperEnum


class Notifications(SuperEnum):
    NONE: Final = 0
    IMPORTANT: Final = 1
    ALL: Final = 2
