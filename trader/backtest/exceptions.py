
class PositionError(Exception):
    def __init__(self, msg):
        super(PositionError, self).__init__(msg)


class NotEnoughFundsError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class LiquidationError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
    