from __future__ import annotations

import plotly.graph_objects as go
import numpy as np

from trader.ui.enumerate import Graph


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
