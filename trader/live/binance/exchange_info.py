from typing import Any

from trader.live.binance.symbol_info import BinanceFuturesSymbolInfo, BinanceSpotSymbolInfo
from trader.live.binance.asset_info import BinanceAssetInfo
from trader.live.binance.rate_limit import BinanceRateLimit


class BinanceSpotExchangeInfo:

    def __init__(self, info: dict[str, Any]):
        self.timezone: str = info['timezone']
        self.server_time: int = info['serverTime']

        self.rate_limits = [BinanceRateLimit(rate_limit) for rate_limit in info['rateLimits']]
        self.exchange_filters: list = info['exchangeFilters']
        self.symbols = [BinanceSpotSymbolInfo(symbol_info) for symbol_info in info['symbols']]

    def get_symbol_info(self, symbol: str):
        for symbol_info in self.symbols:
            if symbol_info.symbol == symbol:
                return symbol_info


class BinanceFuturesExchangeInfo:

    def __init__(self, info: dict[str, Any]):
        self.timezone: str = info['timezone']
        self.server_time: int = info['serverTime']
        self.futures_type: str = info['futuresType']

        self.rate_limits = [BinanceRateLimit(rate_limit) for rate_limit in info['rateLimits']]
        self.exchange_filters: list = info['exchangeFilters']
        self.assets = [BinanceAssetInfo(asset_info) for asset_info in info['assets']]
        self.symbols = [BinanceFuturesSymbolInfo(symbol_info) for symbol_info in info['symbols']]

    def get_asset_info(self, asset: str):
        for asset_info in self.assets:
            if asset_info.asset == asset:
                return asset_info

    def get_symbol_info(self, symbol: str):
        for symbol_info in self.symbols:
            if symbol_info.symbol == symbol:
                return symbol_info
