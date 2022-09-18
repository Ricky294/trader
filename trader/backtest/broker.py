from __future__ import annotations

import copy
from typing import Iterable

from trader.backtest.model import calculate_position_profit, is_position_liquidated

from trader.core.const import TimeInForce, Side, OrderStatus
from trader.core.exception import PositionError, BalanceError, SymbolError, InvalidOrder, LiquidationError
from trader.core.interface import FuturesBroker

from trader.core.model import (
    Balance,
    Position,
    Order,
    StopMarketOrder,
    TakeProfitMarketOrder,
    MarketOrder,
    LimitOrder,
    StopLimitOrder,
    TakeProfitLimitOrder,
    is_add_order,
)

from trader.core.model import POSITION_CLOSE, POSITION_ENTRY

from trader.data.model import Percentage, Candles, Symbol
from util.filter_util import remove_none
from util.generate import generate_uuid4
from util.list_util import remove_elements, remove_all


def is_order_filled(
        order: Order,
        open_price: float,
        high_price: float,
        low_price: float,
):
    price = order.stop_price or order.price or open_price

    return low_price <= price <= high_price


def get_filled_orders(
        open_price: float,
        high_price: float,
        low_price: float,
        open_orders: Iterable[Order],
) -> list[Order]:
    """
    Returns all filled orders in the order they got filled.

    An order is fulfilled if:
     * Order type is Market
     * Order stop price is between high and low price.
     * Order price is between high and low price.

    Fill order:
     * MARKET type orders are always filled first.
     * Orders with stop price and price values filled based on the absolute distance of open_price

    Note: This function does not takes into consideration open positions and required balances or anything else.

    :param open_price: Open price.
    :param high_price: High price.
    :param low_price: Low price.
    :param open_orders: Open orders.

    Examples:
    --------
    >>> ord1 = StopMarketOrder(id=1, symbol=Symbol('BTC', 'USD'), side=Side.SELL, stop_price=0.8)
    >>> ord2 = MarketOrder(id=2, symbol=Symbol('BTC', 'USD'), side=Side.BUY, quantity=1, amount=1, reduce_only=False)
    >>> ord3 = TakeProfitMarketOrder(id=3, symbol=Symbol('BTC', 'USD'), side=Side.SELL, stop_price=1.2)

    >>> filled_orders = get_filled_orders(
    ...     open_price=0.9,
    ...     high_price=1.1,
    ...     low_price=0.7,
    ...     open_orders=(ord1, ord2, ord3),
    ... )

    >>> filled_orders[0].id == 2 and filled_orders[1].id == 1 and len(filled_orders) == 2
    True

    """

    def get_sort_filled_orders(orders: Iterable[Order]):
        def filled_orders_with_weight():
            for order in orders:
                """
                In case of the following order types price should equal:
                 * Market = open_price
                 * Limit = order.price
                 * Stop market & limit, Take profit market & limit = order.stop_price
                """
                price = order.stop_price or order.price or open_price

                if low_price <= price <= high_price:
                    yield order, abs(price - open_price)

        return [
            filled_order for filled_order, weight
            in sorted(filled_orders_with_weight(), key=lambda tup: tup[1])
        ]

    return get_sort_filled_orders(open_orders)


def calculate_quantity(
        amount: float,
        price: float
) -> float:
    """
    Calculates quantity.

    :param amount: Asset amount to spend on position.
    :param price: Unit share price
    :return: amount / price

    :examples:
    >>> calculate_quantity(amount=1000, price=100)
    10.0

    >>> calculate_quantity(amount=100, price=1000)
    0.1
    """

    return amount / price


def calculate_amount(
        quantity: float,
        price: float
) -> float:
    """
    Calculates quantity.

    :param quantity: Asset amount to spend on position.
    :param price: Unit share price
    :return: quantity * price

    :examples:
    >>> calculate_amount(quantity=2, price=100)
    200

    >>> calculate_amount(quantity=5, price=200)
    1000
    """

    return quantity * price


def calculate_fee(
        amount: float,
        fee_rate: float,
        leverage: int,
) -> float:
    """
    Fee calculation formula:
        amount * fee_rate * leverage

    :param amount: Traded amount of asset.
    :param fee_rate: Applied fee rate (percentage / 100).
    :param leverage: Applied leverage (positive integer)
    :return: fee

    >>> calculate_fee(amount=100, fee_rate=.01, leverage=1)
    1.0

    >>> calculate_fee(amount=100, fee_rate=.01, leverage=10)
    10.0
    """
    return amount * fee_rate * leverage


class BacktestFuturesBroker(FuturesBroker):

    def __init__(
            self,
            balances: dict[str, float],
            symbol_leverage_pair: dict[Symbol, int],
            maker_fee_percentage=0.0,
            taker_fee_percentage=0.0,
    ):
        """
        Backtest broker currently only supports one balance and one symbol.

        Maker fee is applied if the order goes into the order book (limit type orders)

        Taker fee is applied if the order fills immediately (market type orders)
        """

        if len(balances) != 1:
            raise ValueError('Multiple balance is not supported. Please provide only one.')

        if len(symbol_leverage_pair) != 1:
            raise ValueError('Symbol with leverage dictionary must include only one key-value pair.')

        super().__init__()

        self.maker_fee_percentage = maker_fee_percentage
        self.taker_fee_percentage = taker_fee_percentage

        self.symbols: tuple[Symbol, ...] = tuple(symbol for symbol in symbol_leverage_pair.keys())

        self._temp_balances: dict[str, float] = balances
        self._balances: dict[str, Balance] = {}

        self._leverages: dict[Symbol, int] = symbol_leverage_pair

        self._positions: dict[Symbol, Position] = {symbol: None for symbol in self.symbols}
        self.open_orders: dict[Symbol, list[Order]] = {symbol: [] for symbol in self.symbols}

    def _post_init(self, candles: Candles):
        """Called by Strategy to initialize Balance"""
        balances = [
            Balance(create_time=candles.times[0], asset=asset, total=amount, available=amount)
            for asset, amount in self._temp_balances.items()
        ]
        self._balances.update({balance.asset: balance for balance in balances})
        self.balance_history.extend(balances)
        del self._temp_balances

    @property
    def assets(self) -> tuple[str, ...]:
        return tuple(asset for asset in self._balances.keys())

    def cancel_orders(self, symbol: Symbol) -> list[Order]:
        self.__validate_symbol(symbol)
        orders = self.open_orders[symbol]

        canceled_orders = remove_all(orders)
        self._on_orders_cancel(canceled_orders)
        return canceled_orders

    def close_position_market(self, symbol: Symbol):
        position = self._get_open_position_or_raise_error(symbol=symbol)

        order = MarketOrder.close_position(
            position=position,
            create_time=self._candles.latest_time,
        )

        self._on_orders_create([order])
        return order

    def close_position_limit(self, symbol: Symbol, price: float, time_in_force: TimeInForce = TimeInForce.GTC):
        position = self._get_open_position_or_raise_error(symbol=symbol)

        order = LimitOrder.close_position(
            position=position,
            price=price,
            time_in_force=time_in_force,
            create_time=self._candles.latest_time,
        )

        self._on_orders_create([order])
        return order

    def __validate_symbol(self, symbol: Symbol):
        if symbol not in self.symbols:
            raise SymbolError(
                f'Unsupported symbol: {symbol}.\n'
                f'Supported symbols: {self.symbols}'
            )

    def check_position_liquidation(self, position: Position | None, balance: Balance):
        if position and position.is_open:
            if is_position_liquidated(
                available_balance=balance.available,
                high_price=self._candles.latest_high_price,
                low_price=self._candles.latest_low_price,
                position=position,
            ):
                raise LiquidationError

    def _get_filled_orders(self, orders: Iterable[Order]):
        return get_filled_orders(
            open_price=self._candles.latest_open_price,
            high_price=self._candles.latest_high_price,
            low_price=self._candles.latest_low_price,
            open_orders=orders,
        )

    def _is_order_filled(self, order: Order):
        return is_order_filled(
            open_price=self._candles.latest_open_price,
            high_price=self._candles.latest_high_price,
            low_price=self._candles.latest_low_price,
            order=order,
        )

    def __call__(self, candles: Candles):
        self._candles = candles[:-1]
        self._next_candles = candles

        symbol = self._candles.symbol
        balance = self._balances[symbol.quote]
        open_orders = self.open_orders[symbol]

        filled_orders = self._get_filled_orders(open_orders)

        filled_stop_limit_orders = [
            sl_order for sl_order in filled_orders
            if isinstance(sl_order, StopLimitOrder | TakeProfitLimitOrder)
        ]
        remove_elements(open_orders, filled_stop_limit_orders)

        limit_orders = [
            order.to_limit_order(create_time=self._candles.latest_time)
            for order in filled_stop_limit_orders
        ]
        self._on_orders_create(limit_orders)
        filled_orders.extend(self._get_filled_orders(limit_orders))

        self.check_position_liquidation(position=self._positions[symbol], balance=balance)

        for order in filled_orders:
            position = self._positions[symbol]
            leverage = self._leverages[symbol]

            fee = calculate_fee(
                amount=position.amount if order.close_position else order.amount,
                fee_rate=self.taker_fee_rate if order.is_taker else self.maker_fee_rate,
                leverage=leverage,
            )

            # There is an open position
            if position and position.is_open:
                id = position.id
                profit = (
                    position.profit
                    + calculate_position_profit(position=position, current_price=self._candles.latest_close_price)
                )
                position_side = position.side
                if is_add_order(order):
                    quantity = position.quantity + order.quantity
                    amount = position.amount + order.amount
                    total_balance = balance.total
                    available_balance = balance.available
                    state = position.state + 1

                # Close order
                elif order.close_position:
                    quantity = position.quantity
                    amount = position.amount

                    total_balance = balance.total + profit
                    available_balance = balance.available + position.amount + profit
                    state = POSITION_CLOSE

                # Reduce order
                else:
                    quantity = position.quantity - order.quantity
                    amount = position.amount - order.amount

                    reduce_rate = order.amount/position.amount
                    if reduce_rate > 1:
                        reduce_rate = 1

                    total_balance = balance.total + profit*reduce_rate
                    available_balance = balance.available + order.amount + profit*reduce_rate
                    state = position.state + 1 if quantity > 0 else POSITION_CLOSE

            # No open position
            else:
                position_side = order.side
                profit = .0
                id = generate_uuid4()
                state = POSITION_ENTRY
                amount = order.amount
                quantity = order.quantity
                total_balance = balance.total
                available_balance = balance.available

            open_orders.remove(order)

            new_position = Position(
                id=id,
                create_time=self._candles.latest_time,
                symbol=order.symbol,
                side=position_side,
                state=state,
                quantity=quantity,
                amount=amount,
                price=order.price or order.stop_price or self._candles.latest_open_price,
                leverage=leverage,
                fee=fee,
                profit=profit,
            )

            self._positions[symbol] = new_position
            self._on_position_change(new_position)

            new_balance = Balance(
                create_time=self._candles.latest_time,
                asset=balance.asset,
                total=total_balance,
                available=available_balance,
            )

            if self._balances[balance.asset] != new_balance:
                self._balances[balance.asset] = new_balance
                self._on_balance_change(new_balance)

        if filled_orders:
            self._on_orders_fill([
                order.copy_with(create_time=self._candles.latest_time, status=OrderStatus.FILLED)
                for order in filled_orders
            ])

        self._on_candle_close(self._positions[symbol])

    @property
    def maker_fee_rate(self) -> float:
        return self.maker_fee_percentage / 100

    @property
    def taker_fee_rate(self) -> float:
        return self.taker_fee_percentage / 100

    def get_balance(self, symbol: Symbol) -> Balance:
        self.__validate_symbol(symbol)

        return self._balances[symbol.quote]

    def get_open_orders(self, symbol: Symbol) -> list[Order]:
        self.__validate_symbol(symbol)

        return self.open_orders[symbol]

    def get_position(self, symbol: Symbol) -> Position | None:
        self.__validate_symbol(symbol)

        position = self._positions[symbol]
        if position and position.is_open:
            return position

    def _on_orders_create(self, orders: list[Order]):
        super()._on_orders_create(orders)

        if orders:
            symbol = orders[0].symbol
            self.open_orders[symbol].extend(orders)

            balance = self._balances[symbol.quote]
            available_balance = balance.available - sum([order.amount for order in orders if is_add_order(order)])

            if available_balance != balance.available:
                new_balance = Balance(
                    create_time=self._next_candles.latest_time,
                    asset=balance.asset,
                    available=available_balance,
                    total=balance.total,
                )
                self._balances[symbol.quote] = new_balance
                self._on_balance_change(new_balance)

    def enter_position(
            self,
            symbol: Symbol,
            amount: float | Percentage,
            side: Side,
            entry_price: float = None,
            time_in_force: TimeInForce = TimeInForce.GTC,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> list[Order]:
        self.__validate_symbol(symbol=symbol)

        balance = self.get_balance(symbol)
        if isinstance(amount, Percentage):
            amount = balance.available * amount.rate
        elif amount <= 0:
            raise ValueError(f'Invalid value for amount: {amount}. It must be greater than 0.')
        elif amount > balance.available * self._leverages[symbol]:
            raise BalanceError(
                f'Unable to create order with {amount} {symbol.quote} '
                f'because leveraged available balance is only '
                f'{balance.available * self._leverages[symbol]} {balance.asset}.'
            )

        if self.get_position(symbol):
            raise PositionError(
                f'Not allowed to enter new position because a {symbol} position is already open.'
            )

        if entry_price:
            if entry_price <= 0:
                raise ValueError(f'Invalid value for entry_price: {entry_price}. It must be greater than 0.')
            price = entry_price
        else:
            price = self._next_candles.latest_open_price

        quantity = calculate_quantity(amount=amount, price=price)

        if entry_price:
            entry_order = LimitOrder(
                create_time=self._next_candles.latest_time,
                symbol=symbol,
                side=side,
                price=price,
                quantity=quantity,
                amount=amount,
                time_in_force=time_in_force,
                reduce_only=False,
            )
        else:
            entry_order = MarketOrder(
                create_time=self._next_candles.latest_time,
                symbol=symbol,
                side=side,
                quantity=quantity,
                amount=amount,
                reduce_only=False,
            )

        take_profit_order = None
        if take_profit_price:
            if take_profit_price <= 0:
                raise ValueError('Parameter take_profit_price must be greater than 0.')

            if side is Side.LONG and take_profit_price <= price:
                raise InvalidOrder(
                    f'Take profit price must be greater than entry_price '
                    f'when opening {side.to_long_short()} position.'
                )
            elif side is Side.SHORT and take_profit_price >= price:
                raise InvalidOrder(
                    f'Take profit price must be less than entry_price '
                    f'when opening {side.to_long_short()} position.'
                )

            take_profit_order = TakeProfitMarketOrder(
                create_time=self._next_candles.latest_time,
                symbol=symbol,
                side=side.opposite(),
                stop_price=take_profit_price,
            )

        stop_loss_order = None
        if stop_loss_order:
            if stop_loss_price <= 0:
                raise ValueError('Parameter stop_loss_price must be greater than 0.')

            if side is Side.LONG and stop_loss_price >= price:
                raise InvalidOrder(
                    f'Stop loss price must be less than entry_price '
                    f'when opening {side.to_long_short()} position.'
                )
            elif side is Side.SHORT and stop_loss_price <= price:
                raise InvalidOrder(
                    f'Stop loss price must be greater than entry_price '
                    f'when opening {side.to_long_short()} position.'
                )

            stop_loss_order = StopMarketOrder(
                create_time=self._next_candles.latest_time,
                symbol=symbol,
                side=side.opposite(),
                stop_price=stop_loss_price,
            )

        orders = remove_none([entry_order, take_profit_order, stop_loss_order])

        self._on_orders_create(orders)

        return orders

    def set_leverage(self, symbol: Symbol, leverage: int):
        self.__validate_symbol(symbol)

        self._leverages[symbol] = leverage
        self._on_leverage_change(symbol, leverage)

    def get_leverage(self, symbol: Symbol) -> int:
        self.__validate_symbol(symbol)

        return self._leverages[symbol]
