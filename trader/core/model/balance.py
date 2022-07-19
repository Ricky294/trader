import pandas as pd

from trader.core.exception import BalanceError
from trader.data.model import Model


class Balance(Model):

    def __init__(self, time: int | float, free: float, asset: str, id=None):
        super().__init__(id, time)
        self.free = float(free)
        self.asset = asset

    @property
    def pd_time(self):
        return pd.to_datetime(self.time, unit='s')

    def _asset_check(self, other):
        if other.asset != self.asset:
            raise BalanceError(
                f'Unable to operate on different assets: '
                f'self ({self.asset!r}) != other ({other.asset!r})'
            )

    def _type_check(self, other):
        if not isinstance(other, Balance):
            raise BalanceError(f'Type of "other" is: {type(other)}, not Balance.')

    def __gt__(self, other):
        """
        True if `self` and `other` is of type Balance
        and `self.free` is greater than `other.free`
        and `self.asset` equals with `other.asset`.

        :param other: Balance object with the same asset type as self.
        :return: bool
        :raises BalanceError: If other is not type of Balance or if the asset value is different.

        :example:
        >>> Balance(100, 'USD') > Balance(100, 'USD')
        False

        >>> Balance(200, 'USD') > Balance(100, 'USD')
        True

        >>> Balance(100, 'XYZ') > Balance(100, 'USD')
        Traceback (most recent call last):
        ...
        trader.core.exception.BalanceError: Unable to operate on different assets: self ('XYZ') != other ('USD')
        """
        self._type_check(other)
        self._asset_check(other)

        return self.free > other.free

    def __ge__(self, other):
        """
        True if `self` and `other` is of type Balance
        and `self.free` is greater than or equal to `other.free`
        and `self.asset` equals with `other.asset`.

        :param other: Balance object with the same asset type as self.
        :return: bool
        :raises BalanceError: If other is not type of Balance or if the asset value is different.

        :example:
        >>> Balance(100, 'USD') >= Balance(100, 'USD')
        True

        >>> Balance(200, 'USD') >= Balance(100, 'USD')
        True

        >>> Balance(100, 'XYZ') >= Balance(100, 'USD')
        Traceback (most recent call last):
        ...
        trader.core.exception.BalanceError: Unable to operate on different assets: self ('XYZ') != other ('USD')
        """
        self._type_check(other)
        self._asset_check(other)

        return self.free >= other.free

    def __lt__(self, other):
        """
        True if `self` and `other` is of type Balance
        and `self.free` is less than `other.free`
        and `self.asset` equals with `other.asset`.

        :param other: Balance object with the same asset type as self.
        :return: bool
        :raises BalanceError: If other is not type of Balance or if the asset value is different.

        :example:
        >>> Balance(100, 'USD') < Balance(100, 'USD')
        False

        >>> Balance(200, 'USD') < Balance(100, 'USD')
        False

        >>> Balance(100, 'XYZ') < Balance(100, 'USD')
        Traceback (most recent call last):
        ...
        trader.core.exception.BalanceError: Unable to operate on different assets: self ('XYZ') != other ('USD')
        """
        self._type_check(other)
        self._asset_check(other)

        return self.free < other.free

    def __le__(self, other):
        """
        True if `self` and `other` is of type Balance
        and `self.free` is less than or equal to `other.free`
        and `self.asset` equals with `other.asset`.

        :param other: Balance object with the same asset type as self.
        :return: bool
        :raises BalanceError: If other is not type of Balance or if the asset value is different.

        :example:
        >>> Balance(100, 'USD') <= Balance(100, 'USD')
        True

        >>> Balance(200, 'USD') <= Balance(100, 'USD')
        False

        >>> Balance(100, 'XYZ') <= Balance(100, 'USD')
        Traceback (most recent call last):
        ...
        trader.core.exception.BalanceError: Unable to operate on different assets: self ('XYZ') != other ('USD')
        """
        self._type_check(other)
        self._asset_check(other)

        return self.free <= other.free
