from typing import List

import numpy as np

from .position import BacktestPosition

TIME_INDEX = 0
PRICE_INDEX = 1
QUANTITY_INDEX = 2

EXIT_TIME_INDEX = 3
EXIT_PRICE_INDEX = 4
EXIT_QUANTITY_INDEX = 5

PROFIT_INDEX = 6
SIDE_INDEX = 7
LEVERAGE_INDEX = 8


def add_or_reduce_positions_to_array(positions: List[BacktestPosition]):
    return np.array([
        tuple(time for position in positions for time in position.times[1:-1]),
        tuple(price for position in positions for price in position.prices[1:-1]),
        tuple(quantity for position in positions for quantity in position.quantities[1:-1]),
    ])


def positions_to_array(positions: List[BacktestPosition]):

    return np.array([
        tuple(position.times[0] for position in positions),
        tuple(position.prices[0] for position in positions),
        tuple(position.quantities[0] for position in positions),

        tuple(position.times[-1] for position in positions),
        tuple(position.prices[-1] for position in positions),
        tuple(position.quantities[-1] for position in positions),

        tuple(position.profit() for position in positions),
        tuple(position.side for position in positions),
        tuple(position.leverage for position in positions),
    ])
