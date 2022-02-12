from trader.core.exceptions import TraderException


class NotEnoughFundsError(TraderException):
    def __init__(self, msg):
        super(NotEnoughFundsError, self).__init__(msg)


class LiquidationError(TraderException):
    def __init__(self, msg):
        super(LiquidationError, self).__init__(msg)
    