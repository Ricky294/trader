from typing import Callable, List

import numpy as np


class Plot:

    def __init__(
            self,
            number: int,
            type: str,
            params: List[dict],
            data_callback: Callable[[np.ndarray], np.ndarray],
    ):
        self.number = number
        self.params = params
        self.type = type
        self.data_callback = data_callback
