"""Trader framework core exceptions.

Exceptions:
    - TraderError - Base exception for all below.
    - BrokerError - Invalid broker.
    - SymbolError - Invalid trade symbol.
    - IntervalError - Invalid trade interval.
    - SideError - Invalid order side.
    - OrderTypeError - Invalid order type.
    - PositionError -
    - BalanceError -
    - LiquidationError -
"""
from trader.data.super_enum import Market


class TraderError(Exception):
    """Base exception used by the framework.

    The framework uses custom and unified exceptions which allows handling
    raised exceptions coming from different type of systems in the same way.

    Exceptions derived from this class:
        - BrokerError
        - MarketError
        - SymbolError
        - IntervalError
        - SideError
        - OrderTypeError
        - PositionError
        - BalanceError
        - LeverageError
        - LiquidationError
    """
    def __init__(self, msg):
        super().__init__(msg)


class BrokerError(TraderError):
    """Exception for invalid/unsupported broker."""
    def __init__(self, broker: str):
        super().__init__(f'Invalid broker: {broker}')


class MarketError(TraderError):
    """"Exception for invalid trading market."""
    def __init__(self, market: Market):
        super(MarketError, self).__init__(f'Invalid market value: {market}')


class SymbolError(TraderError):
    """Exception for invalid trading symbol."""
    def __init__(self, symbol: str):
        super().__init__(f'Invalid symbol: {symbol}')


class IntervalError(TraderError):
    """Exception for invalid trading interval."""
    def __init__(self, interval: str):
        super().__init__(f'Invalid interval: {interval}')


class SideError(TraderError):
    """Exception for invalid order side."""
    def __init__(self, interval: str):
        super().__init__(f'Invalid order side: {interval}')


class OrderTypeError(TraderError):
    """Exception for invalid order type."""
    def __init__(self, order_type: str):
        super().__init__(f'Invalid order type: {order_type}')


class PositionError(TraderError):
    """Exception for position issues.

    Raised in scenarios when
        - position is already opened/closed.
        - unable to create position for some reason (e.g.: unsupported symbol).
    """
    def __init__(self, msg):
        super().__init__(msg)


class BalanceError(TraderError):
    """Exception for balance issues.

    Raised in scenarios when
        - balance is not sufficient to create order.
        - asset type is unsupported.
        - unmatched asset values when using comparison operators on Balance objects
        - unmatched asset values when adding/subtracting from a Balance object.
    """
    def __init__(self, msg):
        super().__init__(msg)


class LeverageError(TraderError):
    """Raised when leverage is less than 1 or over the allowed maximum."""
    def __init__(self, msg):
        super().__init__(msg)


class LiquidationError(TraderError):
    """
    Raised when a short/long position gets liquidated.

    Happens when position loss is greater than the available account balance
    (insufficient margin).

    It is a forced action. Position closing order filled as a market order,
    which can lead to slippage with negative account balance.
    """
    def __init__(self, msg):
        super().__init__(msg)
