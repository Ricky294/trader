import numpy as np
import nputils as npu
import talib

from trader.data.model import Candles

from trader.core.indicator import Indicator
from trader.trade import cross


class MFIIndicator(Indicator):
    """Money Flow Index - MFI

    Momentum Indicator
    """

    def __init__(
            self,
            candles: Candles,
            period=14,
            upper_limit=80.0,
            lower_limit=20.0,
    ):
        self.period = period
        self.upper_limit = upper_limit
        self.lower_limit = lower_limit
        super().__init__(candles)

    @property
    def mfi(self):
        return self._current_slice(self._mfi)

    def __call__(self, candles: Candles):
        """
        Calculates Money Flow Index (volume-weighted MFI)

        :param candles: Input data for MFI indicator
        :return: MFIResult - mfi
        """
        self._mfi = talib.MFI(
            candles.high_prices,
            candles.low_prices,
            candles.close_prices,
            candles.volumes,
            timeperiod=self.period,
        )

    def overbought(self) -> np.ndarray:
        """
        True where MFI is greater than upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return self.mfi > self.upper_limit

    def oversold(self) -> np.ndarray:
        """
        True where MFI is lower than lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return self.mfi < self.lower_limit

    def cross_to_oversold(self) -> np.ndarray:
        """
        True where MFI crosses below lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.mfi < self.lower_limit)

    def cross_from_oversold(self) -> np.ndarray:
        """
        True where MFI crosses above lower limit.

        Oversold - Signals buy

        :return: bool numpy array
        """
        return cross(self.mfi > self.lower_limit)

    def cross_to_overbought(self) -> np.ndarray:
        """
        True where MFI crosses above upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.mfi > self.upper_limit)

    def cross_from_overbought(self) -> np.ndarray:
        """
        True where MFI crosses below upper limit.

        Overbought - Signals sell

        :return: bool numpy array
        """
        return cross(self.mfi < self.upper_limit)

    def overbought_reversal(self) -> np.ndarray:
        """
        True where MFI is above upper limit and current value is less than previous.

        Overbought - Signals sell

        :return: bool numpy array
        """
        try:
            return self.overbought() & npu.peak_reversal(self.mfi)
        except IndexError:
            return np.full(self.mfi.shape, False)

    def oversold_reversal(self) -> np.ndarray:
        """
        True where MFI is below lower limit and current value is greater than previous.

        Oversold - Signals buy

        :return: bool numpy array
        """
        try:
            return self.oversold() & npu.bottom_reversal(self.mfi)
        except IndexError:
            return np.full(self.mfi.shape, False)
