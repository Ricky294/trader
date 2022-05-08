"""Trader framework core exceptions.

Exceptions:
    - TraderException - Base exception for all below.
    - BrokerError - Invalid broker.
    - SymbolError - Invalid trade symbol.
    - IntervalError - Invalid trade interval.
    - SideError - Invalid order side.
    - OrderTypeError - Invalid order type.
    - PositionError -
    - BalanceError -
    - NotEnoughFundsError -
    - LiquidationError -
"""


class TraderException(Exception):
    """Common base exception for the trader framework."""
    def __init__(self, msg):
        super().__init__(msg)


class BrokerError(TraderException):
    """Exception for invalid/unsupported broker."""
    def __init__(self, broker: str):
        super().__init__(f"Invalid broker: {broker}")


class MarketError(TraderException):
    """Exception for invalid trading market."""
    def __init__(self, market: str):
        super(MarketError, self).__init__(f"Invalid market value: {market}")


class SymbolError(TraderException):
    """Exception for invalid trading symbol."""
    def __init__(self, symbol: str):
        super().__init__(f"Invalid symbol: {symbol}")


class IntervalError(TraderException):
    """Exception for invalid trading interval."""
    def __init__(self, interval: str):
        super().__init__(f"Invalid interval: {interval}")


class SideError(TraderException):
    """Exception for invalid order side."""
    def __init__(self, interval: str):
        super().__init__(f"Invalid order side: {interval}")


class OrderTypeError(TraderException):
    """Exception for invalid order type."""
    def __init__(self, order_type: str):
        super().__init__(f"Invalid order type: {order_type}")


class PositionError(TraderException):
    def __init__(self, msg):
        super().__init__(msg)


class BalanceError(TraderException):
    def __init__(self, msg):
        super().__init__(msg)


class NotEnoughFundsError(TraderException):
    def __init__(self, msg):
        super().__init__(msg)


class LiquidationError(TraderException):
    """"""
    def __init__(self, msg):
        super().__init__(msg)
