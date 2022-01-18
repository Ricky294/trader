from typing import Optional, List
from binance.client import Client

from position import BinancePosition
from symbol_info import BinanceSymbolInfo
from trader.core.enum import OrderType
from trader.core.const.trade_actions import BUY
from trader.core.util.common import round_down


def get_open_position(self, symbol: str) -> Optional[dict]:
    positions: List[dict] = self.client.futures_account()["positions"]

    for position in positions:
        if symbol.upper() == position["symbol"] and float(position["unrealizedProfit"]) != 0.0:
            return position


def get_symbol_info(client: Client, symbol: str):
    symbol = symbol.upper()

    for symbol_info in client.futures_exchange_info()["symbols"]:
        if symbol_info["symbol"] == symbol:
            return BinanceSymbolInfo(**symbol_info)

    raise ValueError(f"Invalid symbol: {symbol}")


def get_position_info(client: Client, symbol: str):
    symbol = symbol.upper()

    for position in client.futures_account()["positions"]:
        if position["symbol"] == symbol:
            return BinancePosition(client=client, **position)

    raise ValueError(f"Symbol with name: {symbol} is not found")


def close_position(client: Client, position: BinancePosition, close_price: float = None):
    close_side = "SELL" if position.side == BUY else "BUY"

    if close_price is None:
        # Can't use closePosition="true" because it can only be used with STOP_MARKET and TAKE_PROFIT_MARKET orders
        client.futures_create_order(
            symbol=position.symbol,
            side=close_side,
            type=str(OrderType.MARKET),
            quantity=str(abs(position.quantity)),
            reduceOnly="true",
        )
    else:
        symbol_info = get_symbol_info(client, position.symbol)
        close_price = round_down(close_price, symbol_info.price_precision)

        client.futures_create_order(
            symbol=position.symbol,
            side=close_side,
            type=str(OrderType.STOP_MARKET),
            stopPrice=close_price,
            closePosition="true",
        )


def cancel_open_orders(client: Client, symbol: str):
    client.futures_cancel_all_open_orders(symbol=symbol)
