from enum import Enum
from typing import Any


class SuperEnum(Enum):

    @classmethod
    def from_value(cls, x):
        """
        Creates enum from its value.

        Example
        -------

        >>> class ColorEnum(SuperEnum):
        ...     RED = 'R'
        ...     GREEN = 'G'
        ...     BLUE = 'B'

        >>> ColorEnum.from_value('R') is ColorEnum.RED
        True

        >>> ColorEnum.from_value('R') is ColorEnum.GREEN
        False
        """
        for e in cls:
            if x == e.value:
                return e
        raise ValueError(
            f'{x!r} is not a valid value. '
            f'Valid values are: {cls.keys()}'
        )

    @classmethod
    def to_dict(cls) -> dict[str, Any]:
        """
        Returns the enum as a dictionary.

        Example
        -------

        >>> class ColorEnum(SuperEnum):
        ...     RED = 'R'
        ...     GREEN = 'G'
        ...     BLUE = 'B'

        >>> ColorEnum.to_dict()
        {'RED': 'R', 'GREEN': 'G', 'BLUE': 'B'}
        """
        return {e.name: e.value for e in cls}

    @classmethod
    def keys(cls) -> list[str]:
        """
        Returns a list of all enum keys.

        Example
        -------

        >>> class ColorEnum(SuperEnum):
        ...     RED = 'R'
        ...     GREEN = 'G'
        ...     BLUE = 'B'

        >>> ColorEnum.keys()
        ['RED', 'GREEN', 'BLUE']
        """
        return cls._member_names_

    @classmethod
    def values(cls) -> list[Any]:
        """
        Returns a list of all the enum values.

        Example
        -------

        >>> class ColorEnum(SuperEnum):
        ...     RED = 'R'
        ...     GREEN = 'G'
        ...     BLUE = 'B'

        >>> ColorEnum.values()
        ['R', 'G', 'B']
        """
        return list(cls._value2member_map_.keys())

    def __ne__(self, other):
        return self.value != other.value

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return repr(self.value)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
