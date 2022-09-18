__all__ = [
    'TraderError',
    'AssetError',
    'BrokerError',
    'MarketError',
    'SymbolError',
    'IntervalError',
    'SideError',
    'OrderTypeError',
    'PositionError',
    'BalanceError',
    'LiquidationError',
    'TimeInForceError',
    'LeverageError',
    'InvalidOrder',
    'InvalidPrice',
]

"""Trader framework core exceptions.

Exceptions:
    - TraderError - Base exception for all the exceptions below.
    - AssetError - Invalid asset.
    - BrokerError - Invalid broker.
    - SymbolError - Invalid trade symbol.
    - IntervalError - Invalid trade interval.
    - SideError - Invalid order side.
    - OrderTypeError - Invalid order type.
    - PositionError -
    - BalanceError -
    - LiquidationError -
    - InvalidOrder - 
    - InvalidPrice -
"""


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
        - InvalidOrder
        - InvalidPrice
    """
    ...


class AssetError(TraderError):

    @classmethod
    def invalid(cls, asset):
        return cls(f'Invalid asset: {asset}')


class InvalidOrder(TraderError):
    ...


class InvalidPrice(TraderError):
    ...


class TimeInForceError(TraderError):
    """Exception for invalid/unsupported time in force."""

    @classmethod
    def invalid(cls, tif):
        return cls(f'Invalid time in force: {tif}')


class BrokerError(TraderError):
    """Exception for invalid/unsupported broker."""

    @classmethod
    def invalid(cls, broker):
        return cls(f'Invalid broker: {broker}')


class MarketError(TraderError):
    """"Exception for invalid trading market."""

    @classmethod
    def invalid(cls, market):
        return cls(f'Invalid market value: {market}')


class SymbolError(TraderError):
    """Exception for invalid trading symbol."""

    @classmethod
    def invalid(cls, symbol):
        return cls(f'Invalid symbol: {symbol}')


class IntervalError(TraderError):
    """Exception for invalid trading interval."""

    @classmethod
    def invalid(cls, interval):
        return cls(f'Invalid interval: {interval}')


class SideError(TraderError):
    """Exception for invalid order side."""

    @classmethod
    def invalid(cls, side):
        return cls(f'Invalid side: {side}')


class OrderTypeError(TraderError):
    """Exception for invalid order type."""

    @classmethod
    def invalid(cls, order_type):
        return cls(f'Invalid order type: {order_type}')


class PositionError(TraderError):
    """Exception for position issues.

    Raised in scenarios when
        - position is already opened/closed.
        - unable to create position for some reason (e.g.: unsupported symbol).
    """
    @classmethod
    def no_position_to_close(cls):
        return cls(f'No position to close!')


class BalanceError(TraderError):
    """Exception for balance issues.

    Raised in scenarios when
        - balance is not sufficient to create order.
        - asset type is unsupported.
        - unmatched asset values when using comparison operators on Balance objects
        - unmatched asset values when adding/subtracting from a Balance object.
    """
    ...


class LeverageError(TraderError):
    """Raised when leverage is less than 1 or over the allowed maximum."""

    @classmethod
    def invalid(cls, leverage):
        return cls(f'Invalid leverage value: {leverage}')


class LiquidationError(TraderError):
    """
    Raised when a short/long position gets liquidated.

    Happens when position loss is greater than the available account balance
    (insufficient margin).

    It is a forced action. Position closing order filled as a market order,
    which can lead to slippage with negative account balance.
    """
    ...
