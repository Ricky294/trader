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

        filters: list[dict] = kwargs["filters"]
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

        self.order_types: list[str] = kwargs["orderTypes"]
        self.time_in_force: list[str] = kwargs["timeInForce"]
