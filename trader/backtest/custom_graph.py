from enum import Enum

import numpy as np


class Graph(Enum):
    CAPITAL = "CAPITAL"
    PROFIT = "PROFIT"
    CANDLESTICK = "CANDLESTICK"
    NEW = "NEW"


class CustomGraph:

    def __init__(
            self,
            figure_index: int,
            plot_type: str,
            plot_params: dict,
            y_data: np.ndarray,
    ):
        self.figure_index = figure_index
        self.plot_type = plot_type
        self.plot_params = plot_params
        self.y_data = y_data
