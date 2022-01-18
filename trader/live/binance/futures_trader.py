from typing import Dict, List, Optional

from binance.client import Client

from ...core.interface import FuturesTrader
from ...core.const.trade_actions import BUY
from ...core.model import Order
from ...core.util.trade import create_position

from ..binance import BinanceBalance
from ..binance import BinancePosition
from ..binance import BinanceSymbolInfo
from ..binance.helpers import get_symbol_info, get_position_info


class BinanceFuturesTrader(FuturesTrader):

    def __init__(self, client: Client):
        self.client = client

    def close_position(self, symbol: str):
        position = self.get_position(symbol=symbol)

        if position is not None:
            side = "SELL" if position.side == BUY else "BUY"

            order = Order.market(
                symbol=symbol,
                side=side,
                quantity=position.quantity,
            )
            self.client.futures_create_order(**order)

    def get_leverage(self, symbol) -> int:
        return int(get_position_info(self.client, symbol)["leverage"])

    def create_position(
            self,
            symbol: str,
            quantity: float,
            price: float = None,
            take_profit_price: float = None,
            stop_loss_price: float = None,
    ) -> List[Order]:

        orders = create_position(
            symbol=symbol,
            quantity=quantity,
            price=price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price
        )

        symbol_info = self.get_symbol_info(symbol=symbol)
        orders = dict(batchOrders=[order.to_binance_order(symbol_info) for order in orders if order is not None])

        binance_orders = self.client.futures_place_batch_order(**orders)

        return [Order.from_binance(order) for order in binance_orders]

    def create_order(self, order: Order) -> Order:
        symbol_info = self.get_symbol_info(symbol=order.symbol)
        order = self.client.futures_create_order(
            **order.to_binance_order(
                price_precision=symbol_info.price_precision,
                quantity_precision=symbol_info.quantity_precision
            )
        )
        return Order.from_binance(order)

    def cancel_orders(self, *orders: Order) -> List[Order]:
        return [
            self.client.futures_cancel_order(symbol=order.symbol, orderId=order.order_id)
            for order in orders
        ]

    def cancel_symbol_orders(self, symbol: str) -> List[Order]:
        canceled_orders: List[Dict] = self.client.futures_cancel_all_open_orders(
            symbol=symbol
        )

        return [Order.from_binance(order) for order in canceled_orders]

    def get_open_orders(self, symbol: str = None) -> List[Order]:
        open_orders: List[Dict] = self.client.futures_get_open_orders(symbol=symbol)
        return [Order.from_binance(order) for order in open_orders]

    def get_balances(self) -> List[BinanceBalance]:
        balances: List[Dict] = self.client.futures_account_balance()

        return [
            BinanceBalance(
                asset=balance["asset"],
                total=balance["balance"],
                available=balance["withdrawAvailable"],
            )
            for balance in balances
            if float(balance["balance"]) > 0.0
        ]

    def get_balance(self, asset: str) -> BinanceBalance:
        for balance in self.get_balances():
            if balance.asset == asset:
                return balance

        raise ValueError(f"No available {asset!r} balance.")

    def get_positions(self) -> List[BinancePosition]:
        positions: List[Dict] = self.client.futures_account()["positions"]

        return [
            BinancePosition(**position)
            for position in positions
            if float(position["positionAmt"]) != .0
        ]

    def get_position(self, symbol: str) -> Optional[BinancePosition]:
        for position in self.get_positions():
            if position.symbol == symbol:
                return position

    def get_all_symbol_info(self) -> List[BinanceSymbolInfo]:
        exchange_info: dict = self.client.futures_exchange_info()

        return [BinanceSymbolInfo(**symbol_info) for symbol_info in exchange_info["symbols"]]

    def get_symbol_info(self, symbol: str) -> BinanceSymbolInfo:
        return get_symbol_info(self.client, symbol)

    def set_leverage(self, symbol: str, leverage: int):
        self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
