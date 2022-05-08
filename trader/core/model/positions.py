from typing import Iterable

import numpy as np
import pandas as pd

from trader.core.const.trade_actions import BUY
from trader.core.model import Position


class Positions:

    def __init__(self, positions: Iterable[Position]):
        self.positions = positions

        self.symbol = np.array([pos.symbol for pos in positions])

        self.side = np.array(["Long" if pos.side == BUY else "Short" for pos in positions])
        self.money = np.array([pos.money for pos in positions])
        self.quantity = np.array([pos.quantity for pos in positions])
        self.leverage = np.array([pos.leverage for pos in positions])

        self.entry_time = np.array([pos.entry_time for pos in positions])
        self.entry_price = np.array([pos.entry_price for pos in positions])
        self.entry_fee = np.array([pos.entry_fee for pos in positions])

        self.exit_time = np.array([pos.exit_time for pos in positions])
        self.exit_price = np.array([pos.exit_price for pos in positions])
        self.exit_fee = np.array([pos.exit_fee for pos in positions])
        self.profit = np.array([pos.profit for pos in positions])

    @property
    def to_dataframe(self):
        return pd.DataFrame(
            np.array([position.to_list() for position in self.positions]),
            columns=self.columns,
        )

    @property
    def pd_entry_time(self):
        return pd.to_datetime(self.entry_time, unit="s")

    @property
    def pd_exit_time(self):
        return pd.to_datetime(self.exit_time, unit="s", format="%Y-%m-%d %H:%M:%S")

    @property
    def dt_entry_time(self):
        return pd.to_datetime(self.entry_time, unit="s")

    @property
    def positive_profit(self):
        return self.profit[self.profit >= 0]

    @property
    def negative_profit(self):
        return self.profit[self.profit < 0]

    @property
    def positive_profit_time(self):
        return self.exit_time[self.profit >= 0]

    @property
    def pd_positive_profit_time(self):
        return pd.to_datetime(self.positive_profit_time, unit="s")

    @property
    def negative_profit_time(self):
        return self.exit_time[self.profit < 0]

    @property
    def pd_negative_profit_time(self):
        return pd.to_datetime(self.negative_profit_time, unit="s")

    @property
    def columns(self):
        return [
            "Symbol", "Entry time", "Entry price",
            "Money", "Quantity", "Side", "Entry fee", "Leverage",
            "Exit time", "Exit price", "Exit fee", "Profit",
        ]

    def to_list(self, time_format: str = "pd"):
        if time_format == "ts":
            entry_time = self.entry_time
            exit_time = self.exit_time
        elif time_format == "pd":
            entry_time = self.pd_entry_time
            exit_time = self.pd_exit_time
        else:
            raise ValueError("Format param must be 'ts' or 'pd'.")

        return [
            self.symbol, entry_time, self.entry_price,
            self.money, self.quantity, self.side, self.entry_fee, self.leverage,
            exit_time, self.exit_price, self.exit_fee, self.profit,
        ]

    def to_dict(self):
        return {col: data for col, data in zip(self.columns, self.to_list())}

    def to_records(self, time_format: str = "ts"):
        return [pos.to_dict(time_format) for pos in self.positions]

    def __iter__(self):
        return self.positions
