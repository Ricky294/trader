from typing import Any


class BinanceRateLimit:

    def __init__(self, rate_limit: dict[str, Any]):
        self.type: str = rate_limit['rateLimitType']
        self.interval: str = rate_limit['interval']
        self.interval_num: int = rate_limit['intervalNum']
        self.limit: int = rate_limit['limit']