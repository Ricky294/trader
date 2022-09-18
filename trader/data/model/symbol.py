from dataclasses import dataclass


@dataclass(eq=True, unsafe_hash=True)
class Symbol:
    """Class which represents a currency pair also called as symbol.

    A symbol typically consists of a base & a quote currency
    like EUR/USD.
    """

    __slots__ = '_base', '_quote'

    def __init__(self, base: str, quote: str):
        """Creates a symbol from a `base` & `quote` currency.

        For example EUR/USD in which `base` is EUR and `quote` currency is USD.

        Example:
        -------
        >>> Symbol('EUR', 'USD')
        EUR/USD

        :param base: Base currency (e.g. 'EUR')
        :param quote: Quote currency (e.g. 'USD')
        """

        self._base = base.upper()
        self._quote = quote.upper()

    @classmethod
    def from_pair(cls, pair: str):
        """Creates a symbol from a currency `pair`.

        For example in EUR/USD, `base` currency is EUR and `quote` currency is USD.

        Example:
        -------
        >>> Symbol.from_pair('EUR/USD')
        EUR/USD

        :param pair: Concatenated value of a base & quote currency, separated by '/' character (e.g. 'EUR/USD')
        """

        try:
            return cls(*pair.split('/'))
        except TypeError as e:
            raise ValueError('A symbol object consists of a base and a quote currency separated by a "/" character.') \
                from e

    @property
    def base(self):
        """Returns base currency.

        For example in EUR/USD, the base currency is EUR.
        """

        return self._base

    @property
    def quote(self):
        """
        Returns quote currency.

        For example in EUR/USD, the quote currency is USD.
        """
        return self._quote

    @property
    def pair(self) -> str:
        """Concatenates self.base & self.quote without '/'.

        Example:
        -------
        >>> Symbol('EUR', 'USD').pair
        EURUSD
        """
        return self.base + self.quote

    def __str__(self):
        return f'{self.base}/{self.quote}'

    def __repr__(self):
        return f'{self.base}/{self.quote}'
