from __future__ import annotations

from binance.exceptions import BinanceAPIException
from binance.client import Client

from trader.core.const import Side, TimeInForce
from trader.core.model import Order
from trader.core.model.order import StopMarketOrder, TakeProfitMarketOrder, LimitOrder, MarketOrder

from trader.data.model import Percentage, Candles, Symbol

from trader.live.broker import LiveFuturesBroker
from trader.live.binance.balance import BinanceBalance
from trader.live.binance.exchange_info import BinanceFuturesExchangeInfo
from trader.live.binance.position import BinancePosition

from util.filter_util import remove_none

from trader.core.exception import *


def localize_binance_exception(e: BinanceAPIException):
    if e.code in (-1108,):
        raise AssetError(e.message) from e
    elif e.code in (-1114, -1115):
        raise TimeInForceError(e.message) from e
    elif e.code in (-1116,):
        raise OrderTypeError(e.message) from e
    elif e.code in (-1117,):
        raise SideError(e.message) from e
    elif e.code in (-1120,):
        raise IntervalError(e.message) from e
    elif e.code in (-1121,):
        raise SymbolError(e.message) from e
    elif e.code in (-2018, -2019, -4044):
        raise BalanceError(e.message) from e
    elif e.code in (-2027, -2028, -4028):
        raise LeverageError(e.message) from e
    elif e.code in (-4060,):
        raise SideError(e.message) from e
    elif e.code in (-4062,):
        raise InvalidOrder(e.message) from e
    elif e.code in (-4165,):
        raise IntervalError(e.message) from e
    raise


class BinanceFuturesBroker(LiveFuturesBroker):

    def __init__(
            self,
            symbol_leverage_pair: dict[Symbol, int],
            **client_kwargs
    ):
        super().__init__()
        self.client = Client(**client_kwargs)

        for symbol, leverage in symbol_leverage_pair.items():
            self.set_leverage(symbol=symbol, leverage=leverage)

        self.balance_history.extend([
            BinanceBalance.from_dict(balance)
            for balance in self.client.futures_account_balance() if float(balance['balance']) > .0
        ])

    def __call__(self, candles: Candles):
        self._candles = candles

        position = self.get_position(candles.symbol)
        self._on_candle_close(position)

    def _get_latest_price(self, symbol: Symbol):
        return float(self.client.futures_symbol_ticker(symbol=symbol.pair)['price'])

    def close_position_market(self, symbol: Symbol):
        position = self._get_open_position_or_raise_error(symbol=symbol)

        order = MarketOrder.close_position(position=position)

        return self.create_orders([order])[0]

    def close_position_limit(self, symbol: Symbol, price: float, time_in_force: TimeInForce = TimeInForce.GTC):
        position = self._get_open_position_or_raise_error(symbol=symbol)

        order = LimitOrder.close_position(position=position, price=price, time_in_force=time_in_force)

        return self.create_orders([order])[0]

    def create_orders(self, orders: list[Order]):
        raw_orders = [order.to_binance() for order in orders]
        binance_orders = [self.client.futures_create_order(**order) for order in raw_orders]

        orders = [Order.from_binance(order) for order in binance_orders]

        self._on_orders_create(orders)
        return orders

    def enter_position(
            self,
            symbol: Symbol,
            amount: float | Percentage,
            side: Side,
            entry_price: float = None,
            time_in_force: TimeInForce = TimeInForce.GTC,
            take_profit_price: float = None,
            stop_loss_price: float = None,
            trailing_stop_rate: float = None,
            trailing_stop_activation_price: float = None,
    ):
        position = self.get_position(symbol)
        if position:
            raise PositionError(
                f'Cannot create a {symbol} position, because there is already an open {symbol} position.'
            )

        if entry_price:
            quantity = amount / entry_price
            entry_order = LimitOrder(
                symbol=symbol,
                side=side,
                price=entry_price,
                time_in_force=time_in_force,
                amount=amount,
                quantity=quantity,
                reduce_only=False,
            )
        else:
            quantity = amount / self._get_latest_price(symbol=symbol)
            entry_order = MarketOrder(
                symbol=symbol,
                side=side,
                amount=amount,
                quantity=quantity,
                reduce_only=False,
            )

        take_profit_order = None
        if take_profit_price:
            take_profit_order = TakeProfitMarketOrder(
                symbol=symbol,
                side=side.opposite(),
                stop_price=take_profit_price,
            )

        stop_loss_order = None
        if stop_loss_price:
            stop_loss_order = StopMarketOrder(
                symbol=symbol,
                side=side.opposite(),
                stop_price=stop_loss_price,
            )

        return self.create_orders(remove_none([entry_order, take_profit_order, stop_loss_order]))

    def cancel_orders(self, symbol: Symbol) -> list[Order]:
        raw_orders = self.client.futures_get_open_orders(symbol=symbol.pair)
        orders = [Order.from_binance(raw_order) for raw_order in raw_orders]
        self.client.futures_cancel_all_open_orders(symbol=symbol.pair)
        self._on_orders_cancel(orders)
        return orders

    def get_open_orders(self, symbol: Symbol = None) -> list[Order]:
        open_orders: list[dict] = self.client.futures_get_open_orders(symbol=symbol.pair)
        return [Order.from_binance(order) for order in open_orders]

    def get_balance(self, symbol: Symbol) -> BinanceBalance:
        asset = symbol.quote.upper()

        for balance in self.client.futures_account_balance():
            if balance['asset'] == asset:
                return BinanceBalance.from_dict(balance)
        raise BalanceError(f'Cannot find {asset!r} balance on Binance.')

    def get_exchange_info(self):
        return BinanceFuturesExchangeInfo(self.client.futures_exchange_info())

    def get_position(self, symbol: Symbol) -> BinancePosition | None:
        for position in self.client.futures_account()['positions']:
            if position['symbol'] == symbol.pair:
                position['symbol'] = symbol
                return None if float(position['positionAmt']) == 0 else BinancePosition.from_dict(position)

        raise SymbolError(f'Cannot find symbol named: {symbol} on Binance.')

    def set_leverage(self, symbol: Symbol, leverage: int) -> None:
        self.client.futures_change_leverage(symbol=symbol.pair, leverage=leverage)
        self._on_leverage_change(symbol, leverage)

    def get_leverage(self, symbol: Symbol) -> int:
        for position in self.client.futures_account()['positions']:
            if position['symbol'] == symbol.pair:
                return int(position['leverage'])

        raise SymbolError(f'Cannot find symbol named: {symbol} on Binance.')
