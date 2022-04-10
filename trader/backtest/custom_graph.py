from __future__ import annotations

from enum import Enum

import plotly.graph_objects as go
import numpy as np


class Graph(Enum):
    CAPITAL = 0
    PROFIT = 1
    MAIN = 2
    NEW = 3


class CustomGraph:

    def __init__(
            self,
            selected: Graph,
            type,
            params: dict,
            y: np.ndarray | int | float,
    ):
        self.selected = selected
        self.type = getattr(go, type.capitalize()) if isinstance(type, str) else type
        self.params = params
        self.y = y
