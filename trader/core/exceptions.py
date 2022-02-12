
class TraderException(Exception):
    def __init__(self, msg):
        super(TraderException, self).__init__(msg)


class SymbolError(TraderException):
    def __init__(self, msg):
        super(SymbolError, self).__init__(msg)


class PositionError(TraderException):
    def __init__(self, msg):
        super(PositionError, self).__init__(msg)


class BalanceError(TraderException):
    def __init__(self, msg):
        super(BalanceError, self).__init__(msg)
