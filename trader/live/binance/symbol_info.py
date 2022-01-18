from typing import List, Dict

# Example:
# {
# 'symbol': 'BTCUSDT', 'pair': 'BTCUSDT', 'contractType': 'PERPETUAL', 'deliveryDate': 4133404800000,
# 'onboardDate': 1569398400000, 'status': 'TRADING', 'maintMarginPercent': '2.5000', 'requiredMarginPercent': '5.0000',
# 'baseAsset': 'BTC', 'quoteAsset': 'USDT', 'marginAsset': 'USDT', 'pricePrecision': 2, 'quantityPrecision': 3,
# 'baseAssetPrecision': 8, 'quotePrecision': 8, 'underlyingType': 'COIN', 'underlyingSubType': [], 'settlePlan': 0,
# 'triggerProtect': '0.0500', 'liquidationFee': '0.030000', 'marketTakeBound': '0.05',
# 'filters': [
#     {'minPrice': '556.72', 'maxPrice': '4529764', 'filterType': 'PRICE_FILTER', 'tickSize': '0.01'},
#     {'stepSize': '0.001', 'filterType': 'LOT_SIZE', 'maxQty': '1000', 'minQty': '0.001'},
#     {'stepSize': '0.001', 'filterType': 'MARKET_LOT_SIZE', 'maxQty': '300', 'minQty': '0.001'},
#     {'limit': 200, 'filterType': 'MAX_NUM_ORDERS'},
#     {'limit': 10, 'filterType': 'MAX_NUM_ALGO_ORDERS'},
#     {'notional': '5', 'filterType': 'MIN_NOTIONAL'},
#     {'multiplierDown': '0.9500', 'multiplierUp': '1.0500', 'multiplierDecimal': '4', 'filterType': 'PERCENT_PRICE'}
# ],
# 'orderTypes': ['LIMIT', 'MARKET', 'STOP', 'STOP_MARKET', 'TAKE_PROFIT', 'TAKE_PROFIT_MARKET', 'TRAILING_STOP_MARKET'],
# 'timeInForce': ['GTC', 'IOC', 'FOK', 'GTX']
# }
from trader.core.model import SymbolInfo


class PriceFilter:
    def __init__(self, min_price: float, max_price: float, tick_size: float):
        self.min_price = float(min_price)
        self.max_price = float(max_price)
        self.tick_size = float(tick_size)


class LimitLotSizeFilter:
    def __init__(self, step_size: float, max_quantity: float, min_quantity: float):
        self.max_quantity = float(max_quantity)
        self.min_quantity = float(min_quantity)
        self.step_size = float(step_size)


class MarketLotSizeFilter:
    def __init__(self, step_size: float, max_quantity: float, min_quantity: float):
        self.max_quantity = float(max_quantity)
        self.min_quantity = float(min_quantity)
        self.step_size = float(step_size)


class PercentPriceFilter:
    def __init__(
        self, multiplier_up: float, multiplier_down: float, multiplier_decimal: int
    ):
        self.multiplier_up = float(multiplier_up)
        self.multiplier_down = float(multiplier_down)
        self.multiplier_decimal = float(multiplier_decimal)


class BinanceSymbolInfo(SymbolInfo):

    def __init__(self, **kwargs):
        super().__init__(
            symbol=kwargs["symbol"],
            quantity_precision=kwargs["quantityPrecision"],
            price_precision=kwargs["pricePrecision"]
        )
        self.base_asset: str = kwargs["baseAsset"]
        self.quote_asset: str = kwargs["quoteAsset"]
        self.margin_asset: str = kwargs["marginAsset"]
        self.base_asset_precision: int = kwargs["baseAssetPrecision"]
        self.quote_precision: int = kwargs["quotePrecision"]
        self.underlying_type: str = kwargs["underlyingType"]

        filters: List[Dict] = kwargs["filters"]
        for flt in filters:
            if "PRICE_FILTER" in flt:
                self.price_filter = PriceFilter(
                    max_price=flt["maxPrice"],
                    min_price=flt["minPrice"],
                    tick_size=flt["tickSize"],
                )
            elif "LOT_SIZE" in flt:
                self.limit_lot_size_filter = LimitLotSizeFilter(
                    max_quantity=flt["maxQty"],
                    min_quantity=flt["minQty"],
                    step_size=flt["stepSize"],
                )
            elif "MARKET_LOT_SIZE" in flt:
                self.limit_lot_size_filter = LimitLotSizeFilter(
                    max_quantity=flt["maxQty"],
                    min_quantity=flt["minQty"],
                    step_size=flt["stepSize"],
                )
            elif "MAX_NUM_ORDERS" in flt:
                self.max_orders = float(flt["limit"])
            elif "MAX_NUM_ALGO_ORDERS" in flt:
                self.max_algo_orders = float(flt["limit"])
            elif "MIN_NOTIONAL" in flt:
                self.minimum_notional = int(flt["notional"])
            elif "PERCENT_PRICE" in flt:
                self.price_percent_filter = PercentPriceFilter(
                    multiplier_up=float(flt["multiplierUp"]),
                    multiplier_down=float(flt["multiplierDown"]),
                    multiplier_decimal=int(flt["multiplierDecimal"]),
                )

        self.order_types: List[str] = kwargs["orderTypes"]
        self.time_in_force: List[str] = kwargs["timeInForce"]
