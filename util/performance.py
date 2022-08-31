import cProfile
import os.path
import pstats
import re
from datetime import datetime
from typing import Callable


def execute_measure_performance(func: Callable):
    profiler = cProfile.Profile()
    profiler.enable()

    func()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()

    if not os.path.exists('performance'):
        os.makedirs('performance')

    file_name = re.sub('[ :.-]', '_', str(datetime.now()))
    stats.dump_stats(f"performance/{file_name}")
