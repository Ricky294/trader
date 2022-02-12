import numpy as np

candles = np.array([
    # open_time, open_price, high_price, low_price, close_price, volume
    [1640991600, 950, 1100, 900, 1000, 100],
    [1640991660, 1000, 1200, 800, 900, 100],
    [1640991720, 900, 1000, 800, 850, 100],
    [1640991780, 850, 1100, 500, 900, 100],
    [1640991840, 900, 1100, 700, 1000, 100],
    [1640991900, 700, 800, 600, 620, 100],
    [1640991960, 620, 1200, 400, 1000, 100],
    [1640992020, 1000, 1500, 950, 1400, 100],
    [1640992080, 1400, 1600, 1100, 1500, 100],
    [1640992140, 1500, 1800, 1200, 1600, 100],
    [1640992200, 1600, 2200, 1550, 1800, 100],
    [1640992260, 1800, 1900, 1400, 1450, 100],
    [1640992320, 1450, 1500, 900, 1000, 100],
    [1640992380, 1000, 1200, 950, 1100, 100],
    [1640992440, 1100, 1150, 800, 900, 100],
], dtype=np.float)