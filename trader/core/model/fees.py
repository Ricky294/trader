from typing import Iterable

import numpy as np


class Fees:

    def __init__(self, entry_fees: Iterable[float], exit_fees: Iterable[float]):
        self.entry_fee = np.array(entry_fees)
        self.exit_fee = np.array(exit_fees)
