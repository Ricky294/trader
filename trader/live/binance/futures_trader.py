from __future__ import annotations

from binance.client import Client

from trader.core.enumerate import OrderSide, TimeInForce
from trader.core.interface import FuturesTrader
from trader.core.model import Order
from trader.core.util.trade import create_orders
from trader.core.exception import BalanceError, PositionError

from .balance import BinanceBalance
from .position import BinancePosition, close_position_market, close_position_limit, take_profit_market, stop_loss_market
from .helpers import get_symbol_info, get_position


class BinanceFuturesTrader(FuturesTrader):

    def __init__(self, client: Client):
        super().__init__()
        self.client = client

    def get_latest_price(self, symbol: str):
        return float(self.client.futures_symbol_ticker(symbol=symbol)['price'])

    def close_position_limit(self, symbol: str, price: float, time_in_force: TimeInForce | str = 'GTC'):
        position = self.get_position(symbol=symbol)

        if position is None:
            raise PositionError('No position to close! Skip creating limit order.')

        info = get_symbol_info(client=self.client, symbol=symbol)
        close_position_limit(
            client=self.client,
            position=position,
            price=price,
            price_precision=info.price_precision,
            time_in_force=time_in_force,
        )

    def close_position_market(self, symbol: str):
        position = self.get_position(symbol=symbol)

        if position is None:
            raise PositionError('No position to close! Skip creating market order.')

        close_position_market(client=self.client, position=position)

    def take_profit_market(self, symbol: str, stop_price: float):
        position = self.get_position(symbol=symbol)

        if position is None:
            raise PositionError('No position to close! Skip creating take profit market order.')

        info = get_symbol_info(client=self.client, symbol=symbol)
        take_profit_market(
            client=self.client,
            position=position,
            stop_price=stop_price,
            price_precision=info.price_precision
        )

    def stop_loss_market(self, symbol: str, stop_price: float):
        position = self.get_position(symbol=symbol)

        if position is None:
            raise PositionError('No position to close! Skip creating stop loss market order.')

        info = get_symbol_info(client=self.client, symbol=symbol)
        stop_loss_market(
            client=self.client,
            position=position,
            stop_price=stop_price,
            price_precision=info.price_precision,
        )

    def __in_position(self, symbol: str):
        return self.get_position(symbol) is not None

    def enter_position(
            self,
            symbol: str,
            money: float,
            side: int | OrderSide,
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ):
        if self.__in_position(symbol):
            raise PositionError(
                f'Creating a {symbol} position is not allowed, because a {symbol} position is already opened.'
            )

        orders = create_orders(
            symbol=symbol,
            money=money,
            side=side,
            price=price,
            profit_price=take_profit_price,
            stop_price=stop_loss_price
        )

        info = get_symbol_info(client=self.client, symbol=symbol)

        if price is None:
            price = self.get_latest_price(symbol=symbol)

        quantity = money / price * leverage

        orders = [order.to_binance_order(
            quantity=quantity,
            quantity_precision=info.quantity_precision,
            price_precision=info.price_precision)
            for order in orders if order is not None
        ]

        self.set_leverage(symbol=symbol, leverage=leverage)

        for order in orders:
            self.client.futures_create_order(**order)

    def cancel_orders(self, symbol: str):
        self.client.futures_cancel_all_open_orders(symbol=symbol)

    def get_open_orders(self, symbol: str = None) -> list[Order]:
        open_orders: list[dict] = self.client.futures_get_open_orders(symbol=symbol)
        return [Order.from_binance(order) for order in open_orders]

    def __get_balances(self) -> list[BinanceBalance]:
        balances: list[dict] = self.client.futures_account_balance()

        return [
            BinanceBalance(
                asset=balance['asset'],
                total=balance['balance'],
                free=balance['withdrawAvailable'],
            )
            for balance in balances
            if float(balance['withdrawAvailable']) > 0.0
        ]

    def get_balance(self, asset: str) -> BinanceBalance:
        for balance in self.__get_balances():
            if balance.asset == asset:
                return balance
        raise BalanceError(f'{asset!r} account balance is 0.')

    def get_position(self, symbol: str) -> BinancePosition | None:
        return get_position(client=self.client, symbol=symbol)

    def set_leverage(self, symbol: str, leverage: int):
        self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
