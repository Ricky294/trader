import pandas as pd

from trader.core.exception import BalanceError


class Balance:

    __slots__ = 'time', 'free', 'asset'

    def __init__(self, time: int, free: float, asset: str):
        """
        Creates a Balance object.

        :param free: Available and free to use amount.
        :param asset: Name of the asset/money/currency etc.
        """
        if float(free) < 0:
            raise BalanceError(f'{asset!r} balance must be greater than 0.')

        self.time = int(time)
        self.free = float(free)
        self.asset = asset

    @property
    def pd_time(self):
        return pd.to_datetime(self.time, unit='s')

    def __str__(self):
        return f'{self.pd_time} - {self.free} {self.asset}'

    def __repr__(self):
        return f'{self.pd_time} - {self.free!r} {self.asset!r}'

    def __asset_check(self, other):
        if other.asset != self.asset:
            raise BalanceError(
                f'Unable to operate on different assets: '
                f'self ({self.asset!r}) != other ({other.asset!r})'
            )

    def __type_check(self, other):
        if not isinstance(other, Balance):
            raise BalanceError(f'Type of "other" is: {type(other)}, not Balance.')

    def __eq__(self, other):
        """
        True if `self` has exactly the same values as `other`, and `other` is instance of Balance.

        :example:
        >>> Balance(100, 'USD') == Balance(100, 'USD')
        True

        >>> Balance(200, 'USD') == Balance(100, 'USD')
        False

        >>> type('Balance2', (), {'free': 100, 'asset': 'USD'})() == Balance(100, 'USD')
        False
        """
        return isinstance(other, Balance) and self.asset == other.asset and self.free == other.free

    def __ne__(self, other):
        """
        True if `self` is has different values than `other`.

        :example:
        >>> Balance(100, 'USD') != Balance(100, 'USD')
        False

        >>> Balance(200, 'USD') != Balance(100, 'USD')
        True

        >>> type('Balance2', (), {'free': 100, 'asset': 'USD'})() != Balance(100, 'USD')
        True
        """
        return not self.__eq__(other)

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
        self.__type_check(other)
        self.__asset_check(other)

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
        self.__type_check(other)
        self.__asset_check(other)

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
        self.__type_check(other)
        self.__asset_check(other)

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
        self.__type_check(other)
        self.__asset_check(other)

        return self.free <= other.free
