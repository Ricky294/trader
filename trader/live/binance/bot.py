from typing import Union

from crypto_data.binance.np.stream import candle_stream
from crypto_data.binance.schema import OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME
from crypto_data.enum.market import Market

from trader.core.interface import TradingBot
from trader.core.strategy import Strategy
from ..binance import BinanceFuturesTrader


class BinanceBot(TradingBot):

    def add_strategy(self, strategy: Strategy):
        if not isinstance(strategy.trader, BinanceFuturesTrader):
            raise ValueError("Trader is not an instance of BinanceFuturesTrader!")
        self.strategy = strategy

    def _run(
            self,
            symbol: str,
            interval: str,
            market: Union[str, Market],
    ):
        candle_stream(
            symbol=symbol,
            interval=interval,
            market=str(market),
            columns=[OPEN_TIME, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, VOLUME],
            candles=self.candles,
            on_candle=lambda stream_candle: None,
            on_candle_close=self.strategy,
        )
