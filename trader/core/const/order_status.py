from typing import Final

from util.super_enum import SuperEnum


class OrderStatus(SuperEnum):
    CANCELED: Final = 'CANCELED'
    EXPIRED: Final = 'EXPIRED'
    FILLED: Final = 'FILLED'
    NEW: Final = 'NEW'
    PARTIALLY_FILLED: Final = 'PARTIALLY_FILLED'
    PENDING_CANCEL: Final = 'PENDING_CANCEL'
    REJECTED: Final = 'REJECTED'
