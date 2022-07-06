from trader.core.log import create_logger
from trader.core.util.common import singleton


@singleton
def get_live_logger():
    return create_logger('trader.live', file_path='logs/live')
