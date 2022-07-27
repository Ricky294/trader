from __future__ import annotations

import os.path
from abc import ABC, abstractmethod
from pathlib import Path

from trader.data.super_enum import Market
from trader.data.log import get_data_logger


class CandleStorage(ABC):

    @staticmethod
    @abstractmethod
    def file_extension(): ...

    @property
    def file_name(self):
        """
        Returns the filename with extension.

        Formula: {symbol}_{interval}_{market}.{extension}
        """
        return f'{self.symbol}_{self.interval}_{str(self.market)}.{self.file_extension()}'.lower()

    @property
    def path(self):
        """Returns database file path."""
        return os.path.join(self.dir_path, self.file_name).replace("\\", "/")

    def __init__(self, dir_path: str, symbol: str, interval: str, market: Market):
        parent_dir = Path(dir_path)
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            get_data_logger().info(f'Created directory: {dir_path!r}.')

        self.dir_path = dir_path
        self.symbol = symbol
        self.interval = interval
        self.market = market

    @abstractmethod
    def append(
            self,
            data,
    ):
        """Appends data to database."""
        ...

    @abstractmethod
    def get(
            self,
    ):
        """Reads data from database."""
        ...
