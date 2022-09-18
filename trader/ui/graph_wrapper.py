from __future__ import annotations

from typing import Iterable

import plotly.graph_objs as go

from trader.ui.const import Graph


class CustomGraph:
    def __init__(
            self,
            graph: Graph,
            graph_object: go.BaseTraceType | Iterable[go.BaseTraceType],
    ):
        self.graph = graph
        self.graph_objects = graph_object
