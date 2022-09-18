class Percentage(float):

    __slots__ = '_p'

    def __init__(self, p: float, /):
        """
        Creates a Percentage type object.

        :param p: Floating point percentage value between 0 and 100.

        :raises ValueError: If `p` is not between 0 and 100.

        Example:

        >>> Percentage(0)
        '0.0%'

        >>> Percentage(10.25)
        '10.25%'

        >>> Percentage(100)
        '100.0%'

        >>> Percentage(101)
        Traceback (most recent call last):
        ValueError: Invalid value: 101. Percentage must be between 0 and 100.
        """

        if 0 <= p <= 100:
            self._p = float(p)
        else:
            raise ValueError(f'Invalid value: {p}. Percentage must be between 0 and 100.')

    @property
    def rate(self) -> float:
        return self._p / 100

    def __str__(self):
        return f'{self._p}%'

    def __repr__(self):
        return repr(str(self))
