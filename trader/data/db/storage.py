from __future__ import annotations

import os.path
from abc import ABC, abstractmethod
from pathlib import Path

import trader.log
from trader.core.const import Market


class CandleStorage(ABC):

    def __init__(self, dir_path: str, symbol: str, interval: str, market: Market):
        parent_dir = Path(dir_path)
        if not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)
            trader.log.core().info(f'Created directory: {dir_path!r}.')

        self.dir_path = dir_path
        self.symbol = symbol
        self.interval = interval
        self.market = market

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
        """Returns db file path."""
        return os.path.join(self.dir_path, self.file_name).replace("\\", "/")

    @abstractmethod
    def append(
            self,
            data,
    ):
        """Appends data to db."""
        ...

    @abstractmethod
    def get(
            self,
    ):
        """Reads data from db."""
        ...