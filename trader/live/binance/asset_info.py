from typing import Any


class BinanceAssetInfo:

    def __init__(self, asset_info: dict[str, Any]):
        self.asset: str = asset_info['asset']
        self.margin_available: bool = asset_info['marginAvailable']
        self.auto_asset_exchange = float(asset_info['autoAssetExchange'])
