import numpy as np
import talib

from ..enum.ohlcv import OHLCV
from ..const.candle_index import (
    HIGH_PRICE_INDEX,
    LOW_PRICE_INDEX,
    CLOSE_PRICE_INDEX, VOLUME_INDEX,
)


class Indicators:

    def __init__(self, candles: np.ndarray):
        self.candles = candles.T

    # --------------------- Overlap indicators --------------------- #

    def BBANDS(self, period=5, nbdev_up=2, nbdev_down=2, ma_type=0, value=OHLCV.CLOSE_PRICE):
        """Bollinger Bands"""
        return talib.BBANDS(
            self.candles[int(value)],
            timeperiod=period,
            nbdev_up=nbdev_up,
            nbdevdn=nbdev_down,
            matype=ma_type
        )

    def SMA(self, period: int, value=OHLCV.CLOSE_PRICE):
        """Simple Moving Average"""
        return talib.SMA(
            self.candles[int(value)],
            timeperiod=period,
        )

    def WMA(self, period: int, value=OHLCV.CLOSE_PRICE):
        """Weighted Moving Average"""
        return talib.WMA(
            self.candles[int(value)],
            timeperiod=period,
        )

    def DEMA(self, period: int, value=OHLCV.CLOSE_PRICE):
        """Exponential Moving Average"""
        return talib.DEMA(
            self.candles[int(value)],
            timeperiod=period,
        )

    # --------------------- Volatility indicators --------------------- #

    def ATR(self, period=14):
        """Average True Range"""
        return talib.ATR(
            self.candles[HIGH_PRICE_INDEX],
            self.candles[LOW_PRICE_INDEX],
            self.candles[CLOSE_PRICE_INDEX],
            timeperiod=period,
        )

    def NATR(self, period=14):
        """Normalized Average True Range"""
        return talib.NATR(
            self.candles[HIGH_PRICE_INDEX],
            self.candles[LOW_PRICE_INDEX],
            self.candles[CLOSE_PRICE_INDEX],
            timeperiod=period
        )

    def TRANGE(self):
        """True Range"""
        return talib.TRANGE(
            self.candles[HIGH_PRICE_INDEX],
            self.candles[LOW_PRICE_INDEX],
            self.candles[CLOSE_PRICE_INDEX],
        )

    # --------------------- Momentum indicators --------------------- #

    def MACD(self, value=OHLCV.CLOSE_PRICE, fast_period=12, slow_period=26, signal_period=9):
        """
        Moving Average Convergence/Divergence
        :return: macd, signal, histogram
        """
        return talib.MACD(
            self.candles[int(value)],
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period,
        )

    # --------------------- Volume indicators --------------------- #

    def AD(self):
        """Chaikin A/D Line"""
        return talib.AD(
            self.candles[HIGH_PRICE_INDEX],
            self.candles[LOW_PRICE_INDEX],
            self.candles[CLOSE_PRICE_INDEX],
            self.candles[VOLUME_INDEX],
        )

    def ADOSC(self, fast_period=3, slow_period=10):
        """Chaikin A/D Oscillator"""
        return talib.ADOSC(
            self.candles[HIGH_PRICE_INDEX],
            self.candles[LOW_PRICE_INDEX],
            self.candles[CLOSE_PRICE_INDEX],
            self.candles[VOLUME_INDEX],
            fastperiod=fast_period,
            slowperiod=slow_period
        )

    def OBV(self, value=OHLCV.CLOSE_PRICE):
        """On Balance Volume"""
        return talib.OBV(
            self.candles[int(value)],
            self.candles[VOLUME_INDEX],
        )
