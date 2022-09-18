from datetime import datetime
from dataclasses import dataclass

from trader.core.model import Balance
from util.format_util import normalize_data_types


@dataclass(frozen=True)
class BinanceBalance(Balance):

    @classmethod
    def from_dict(cls, balance: dict[str, float | str]):
        balance = normalize_data_types(balance)

        return cls(
            create_time=datetime.fromtimestamp(balance['updateTime'] / 1000),
            asset=balance['asset'],
            total=balance['balance'],
            available=balance['withdrawAvailable']
        )
