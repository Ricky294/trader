from typing import Final

from util.super_enum import SuperEnum


class OrderType(SuperEnum):
    MARKET: Final = 'MARKET'
    LIMIT: Final = 'LIMIT'
    STOP_MARKET: Final = 'STOP_MARKET'
    STOP_LIMIT: Final = 'STOP_LIMIT'
    TAKE_PROFIT_MARKET: Final = 'TAKE_PROFIT_MARKET'
    TAKE_PROFIT_LIMIT: Final = 'TAKE_PROFIT_LIMIT'
    TRAILING_STOP_MARKET: Final = 'TRAILING_STOP_MARKET'

    def to_order_class(self):
        from trader.core.model.order import (
            MarketOrder, LimitOrder,
            StopMarketOrder, StopLimitOrder,
            TakeProfitLimitOrder, TakeProfitMarketOrder,
            TrailingStopMarketOrder
        )

        if self is OrderType.MARKET:
            return MarketOrder
        elif self is OrderType.LIMIT:
            return LimitOrder
        elif self is OrderType.STOP_MARKET:
            return StopMarketOrder
        elif self is OrderType.STOP_LIMIT:
            return StopLimitOrder
        elif self is OrderType.TAKE_PROFIT_LIMIT:
            return TakeProfitLimitOrder
        elif self is OrderType.TAKE_PROFIT_MARKET:
            return TakeProfitMarketOrder
        elif self is OrderType.TRAILING_STOP_MARKET:
            return TrailingStopMarketOrder
        raise ValueError(f'No matching order for order type: {self}')

    @classmethod
    def from_binance(cls, order_type: str):
        """
        Returns an OrderType from a binance order type.

        * LIMIT
        * MARKET
        * STOP
        * STOP_MARKET
        * TAKE_PROFIT
        * TAKE_PROFIT_MARKET
        * TRAILING_STOP_MARKET

        :raises ValueError: If ord_type is invalid.

        Examples:
        --------

        >>> OrderType.from_binance('MARKET') is OrderType.MARKET
        True

        >>> OrderType.from_binance('LIMIT') is OrderType.LIMIT
        True

        >>> OrderType.from_binance('STOP') is OrderType.STOP_LIMIT
        True

        >>> OrderType.from_binance('STOP_MARKET') is OrderType.STOP_MARKET
        True

        >>> OrderType.from_binance('TAKE_PROFIT') is OrderType.TAKE_PROFIT_LIMIT
        True

        >>> OrderType.from_binance('TAKE_PROFIT_MARKET') is OrderType.TAKE_PROFIT_MARKET
        True

        >>> OrderType.from_binance('TRAILING_STOP_MARKET') is OrderType.TRAILING_STOP_MARKET
        True
        """

        if order_type == 'MARKET':
            return cls.MARKET
        elif order_type == 'LIMIT':
            return cls.LIMIT
        elif order_type == 'STOP':
            return cls.STOP_LIMIT
        elif order_type == 'STOP_MARKET':
            return cls.STOP_MARKET
        elif order_type in 'TAKE_PROFIT':
            return cls.TAKE_PROFIT_LIMIT
        elif order_type == 'TAKE_PROFIT_MARKET':
            return cls.TAKE_PROFIT_MARKET
        elif order_type == 'TRAILING_STOP_MARKET':
            return cls.TRAILING_STOP_MARKET

        raise ValueError(f'Invalid Binance order type: {order_type}!')

    def to_binance(self) -> str:
        """
        Converts self to a binance compatible order type.

        * LIMIT
        * MARKET
        * STOP
        * STOP_MARKET
        * TAKE_PROFIT
        * TAKE_PROFIT_MARKET
        * TRAILING_STOP_MARKET

        Examples:
        --------

        >>> OrderType.LIMIT.to_binance()
        'LIMIT'

        >>> OrderType.MARKET.to_binance()
        'MARKET'

        >>> OrderType.STOP_LIMIT.to_binance()
        'STOP'

        >>> OrderType.STOP_MARKET.to_binance()
        'STOP_MARKET'

        >>> OrderType.TAKE_PROFIT_LIMIT.to_binance()
        'TAKE_PROFIT'

        >>> OrderType.TAKE_PROFIT_MARKET.to_binance()
        'TAKE_PROFIT_MARKET'

        >>> OrderType.TRAILING_STOP_MARKET.to_binance()
        'TRAILING_STOP_MARKET'
        """

        if self is OrderType.STOP_LIMIT:
            return 'STOP'
        elif self is OrderType.TAKE_PROFIT_LIMIT:
            return 'TAKE_PROFIT'

        return str(self)

    def is_taker(self) -> bool:
        """
        Does not go into the order book (instantly executed).

        Market type order.
        """
        return 'MARKET' in self.value

    def is_maker(self) -> bool:
        """
        Goes into the order book (not instantly executed).

        Limit type order.
        """
        return 'LIMIT' in self.value

    def __int__(self):
        if self.value == 'MARKET':
            return 0
        elif self.value == 'LIMIT':
            return 1
        elif self.value == 'STOP_MARKET':
            return 2
        elif self.value == 'STOP_LIMIT':
            return 3
        elif self.value == 'TAKE_PROFIT_MARKET':
            return 4
        elif self.value == 'TAKE_PROFIT_LIMIT':
            return 5
        elif self.value == 'TRAILING_STOP_MARKET':
            return 6
        raise ValueError(f'Invalid value: {self.value}')
