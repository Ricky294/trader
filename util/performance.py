import cProfile
import pstats
from datetime import datetime
from typing import Callable

from util.file_util import split_path, make_dirs


def measure_performance(
        func: Callable,
        file_name=f"performance/{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}",
        sort_by: str | pstats.SortKey | tuple[str | pstats.SortKey] = 'tottime',
        *func_args,
        **func_kwargs
):
    profiler = cProfile.Profile()

    profiler.enable()
    func(*func_args, **func_kwargs)
    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats(sort_by)
    stats.print_stats()

    if file_name:
        dir_paths = split_path(file_name)[:-1]
        make_dirs(dir_paths)

        stats.dump_stats(file_name)
