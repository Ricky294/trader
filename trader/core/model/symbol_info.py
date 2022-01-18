
class SymbolInfo:

    __slots__ = "symbol", "quantity_precision", "price_precision"

    def __init__(
            self,
            symbol: str,
            quantity_precision: int,
            price_precision: int,
    ):
        self.symbol = symbol
        self.quantity_precision = quantity_precision
        self.price_precision = price_precision
