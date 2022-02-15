from typing import Dict, List, Optional, Union

from binance.client import Client

from trader.core.enum import OrderSide, TimeInForce
from trader.core.interface import FuturesTrader
from trader.core.model import Order
from trader.core.util.trade import create_orders
from trader.core.exception import BalanceError
from trader.core.log import logger

from .balance import BinanceBalance
from .position import BinancePosition, close_position_market, close_position_limit, take_profit_market, stop_loss_market
from .helpers import get_symbol_info, get_position


class BinanceFuturesTrader(FuturesTrader):

    def __init__(self, client: Client):
        self.client = client

    def get_latest_price(self, symbol: str):
        return float(self.client.futures_symbol_ticker(symbol=symbol)["price"])

    def close_position_limit(self, symbol: str, price: float, time_in_force: Union[TimeInForce, str] = "GTC"):
        position = self.get_position(symbol=symbol)

        if position is None:
            logger.warning("No position to close! Skip creating limit order.")
            return

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
            logger.warning("No position to close! Skip creating market order.")
            return

        close_position_market(client=self.client, position=position)

    def take_profit_market(self, symbol: str, stop_price: float):
        position = self.get_position(symbol=symbol)

        if position is None:
            logger.warning("No position to close! Skip creating take profit market order.")
            return

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
            logger.warning("No position to close! Skip creating stop loss market order.")
            return

        info = get_symbol_info(client=self.client, symbol=symbol)
        stop_loss_market(
            client=self.client,
            position=position,
            stop_price=stop_price,
            price_precision=info.price_precision,
        )

    def create_position(
            self,
            symbol: str,
            money: float,
            side: Union[int, OrderSide],
            leverage: int,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ):
        if self.get_position(symbol) is not None:
            logger.warning(
                f"Creating a {symbol} position is not allowed.\n"
                f"Reason: A {symbol} position is already opened."
            )
            return

        orders = create_orders(
            symbol=symbol,
            money=money,
            side=side,
            entry_price=price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price
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

        # self.client.futures_place_batch_order(batchOrders=orders)

    def cancel_orders(self, symbol: str):
        self.client.futures_cancel_all_open_orders(symbol=symbol)

    def get_open_orders(self, symbol: str = None) -> List[Order]:
        open_orders: List[Dict] = self.client.futures_get_open_orders(symbol=symbol)
        return [Order.from_binance(order) for order in open_orders]

    def get_balances(self) -> List[BinanceBalance]:
        balances: List[Dict] = self.client.futures_account_balance()

        return [
            BinanceBalance(
                asset=balance["asset"],
                total=balance["balance"],
                free=balance["withdrawAvailable"],
            )
            for balance in balances
            if float(balance["withdrawAvailable"]) > 0.0
        ]

    def get_balance(self, asset: str) -> BinanceBalance:
        for balance in self.get_balances():
            if balance.asset == asset:
                return balance
        raise BalanceError(f"{asset!r} account balance is 0.")

    def get_position(self, symbol: str) -> Optional[BinancePosition]:
        return get_position(client=self.client, symbol=symbol)

    def set_leverage(self, symbol: str, leverage: int):
        self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
