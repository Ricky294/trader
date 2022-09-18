from typing import Any

from trader.core.const import OrderType, TimeInForce


class BinanceSpotSymbolInfo:

    def __init__(self, symbol_info: dict[str, Any]):
        self.symbol: str = symbol_info['symbol']
        self.status: str = symbol_info['status']

        self.base_asset: str = symbol_info['baseAsset']
        self.base_asset_precision: str = symbol_info['baseAssetPrecision']
        self.base_commission_precision: int = symbol_info['baseCommissionPrecision']

        self.quote_asset: str = symbol_info['quoteAsset']
        self.quote_precision: str = symbol_info['quotePrecision']
        self.quote_asset_precision: int = symbol_info['quoteAssetPrecision']
        self.quote_commission_precision: int = symbol_info['quoteCommissionPrecision']
        self.quote_order_quantity_market_allowed: bool = symbol_info['quoteOrderQtyMarketAllowed']

        self.iceberg_allowed: bool = symbol_info['icebergAllowed']
        self.oco_allowed: bool = symbol_info['ocoAllowed']
        self.allow_trailing_stop: bool = symbol_info['allowTrailingStop']
        self.cancel_replace_allowed: bool = symbol_info['cancelReplaceAllowed']
        self.is_spot_trading_allowed: bool = symbol_info['isSpotTradingAllowed']
        self.is_margin_trading_allowed: bool = symbol_info['isMarginTradingAllowed']
        self.filters: list[dict[str, Any]] = symbol_info['filters']
        self.permissions = symbol_info['permissions']
        self.order_types = [OrderType.from_binance(order_type) for order_type in symbol_info['orderTypes']]


class BinanceFuturesSymbolInfo:

    def __init__(self, symbol_info: dict[str, Any]):
        self.symbol: str = symbol_info['symbol']
        self.pair: str = symbol_info['pair']
        self.contract_type: str = symbol_info['contractType']
        self.delivery_date: int = symbol_info['deliveryDate']
        self.onboard_date: int = symbol_info['onboardDate']
        self.status: str = symbol_info['status']
        self.maint_margin_percent = float(symbol_info['maintMarginPercent'])
        self.required_margin_percent = float(symbol_info['requiredMarginPercent'])
        self.base_asset: str = symbol_info['baseAsset']
        self.quote_asset: str = symbol_info['quoteAsset']
        self.margin_asset: str = symbol_info['marginAsset']
        self.price_precision: str = symbol_info['pricePrecision']
        self.quantity_precision: str = symbol_info['quantityPrecision']
        self.base_asset_precision: str = symbol_info['baseAssetPrecision']
        self.quote_precision: str = symbol_info['quotePrecision']
        self.underlying_type: str = symbol_info['underlyingType']
        self.underlyingSubType: str = symbol_info['underlyingSubType']
        self.settle_plan: int = symbol_info['settlePlan']
        self.trigger_protect = float(symbol_info['triggerProtect'])
        self.liquidation_fee = float(symbol_info['liquidationFee'])
        self.market_take_bound = float(symbol_info['marketTakeBound'])
        self.filters = symbol_info['filters']
        self.order_types = [OrderType.from_binance(order_type) for order_type in symbol_info['orderTypes']]
        self.time_in_force = [TimeInForce.from_value(time_in_force) for time_in_force in symbol_info['timeInForce']]
