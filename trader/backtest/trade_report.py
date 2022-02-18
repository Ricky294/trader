from typing import List

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from trader import MONEY_PRECISION
from trader.core.model import Position
from trader.core.const.candle_index import OPEN_TIME_INDEX
from trader.core.util.common import Storable


class TradeReport(Storable):

    def __init__(
            self,
            start_cash: float,
            positions: List[Position],
            trade_ratio: float,
            candles: np.ndarray,
            interval: str,
            leverage: int,
    ):

        self.candles = candles
        self.start_timestamp = candles[0][OPEN_TIME_INDEX]
        self.end_timestamp = candles[-1][OPEN_TIME_INDEX]

        self.trade_ratio = trade_ratio
        self.interval = interval

        self.start_cash = start_cash
        self.profits = tuple(position.profit() for position in positions)
        self.end_cash = sum(self.profits) + self.start_cash

        self.leverage = leverage

        self.wins = len(tuple(position for position in positions if position.profit() > 0))
        self.losses = len(tuple(position for position in positions if position.profit() < 0))

    @property
    def number_of_candles(self):
        return self.candles.shape[0]

    @property
    def start_time(self):
        return pd.to_datetime(self.start_timestamp, unit='s')

    @property
    def end_time(self):
        return pd.to_datetime(self.end_timestamp, unit='s')

    @property
    def win_rate(self):
        try:
            return self.wins / (self.wins + self.losses)
        except ZeroDivisionError:
            return 0

    @property
    def biggest_win(self):
        return max(self.profits)

    @property
    def biggest_loss(self):
        return min(self.profits)

    @property
    def profit(self):
        return (self.end_cash - self.start_cash) / self.start_cash

    def create_basic_info_table(self):
        return go.Table(
            cells=dict(
                values=[
                    [
                        "Duration",
                        "Number of candles",
                        "Interval",
                        "Leverage",
                    ],
                    [
                        f"{self.start_time} - {self.end_time}",
                        self.number_of_candles,
                        self.interval,
                        f"{self.leverage}x",
                    ]
                ],
            ),
        )

    def create_trade_result_table(self):
        return go.Table(
            cells=dict(
                values=[
                    [
                        "Winner positions",
                        "Loosing positions",
                        "Biggest win",
                        "Biggest loose",
                        "Win rate",
                        "Start cash",
                        "Final cash",
                        "Profit",
                    ],
                    [
                        self.wins,
                        self.losses,
                        f"{self.biggest_win:.{MONEY_PRECISION}f}",
                        f"{self.biggest_loss:.{MONEY_PRECISION}f}",
                        f"{self.win_rate:.{MONEY_PRECISION}%}",
                        f"{self.start_cash:.{MONEY_PRECISION}f}",
                        f"{self.end_cash:.{MONEY_PRECISION}f}",
                        f"{self.profit:.{MONEY_PRECISION}%}",
                    ]
                ],
            ),
        )
