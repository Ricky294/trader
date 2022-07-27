from enum import Enum


class SuperEnum(Enum):

    @classmethod
    def from_str(cls, x: str) -> 'SuperEnum':
        for e in cls:
            if x == e.value:
                return e
        raise ValueError(
            f'{x!r} is not a valid value. '
            f'Valid values are: {cls.keys()}'
        )

    @classmethod
    def to_dict(cls):
        """Returns a dictionary representation of the enum."""
        return {e.name: e.value for e in cls}

    @classmethod
    def keys(cls):
        """Returns a list of all the enum keys."""
        return cls._member_names_

    @classmethod
    def values(cls):
        """Returns a list of all the enum values."""
        return list(cls._value2member_map_.keys())

    def __ne__(self, other):
        return str(self).upper() != str(other).upper()

    def __eq__(self, other):
        return str(self).upper() == str(other).upper()

    def __gt__(self, other):
        return str(self).upper() > str(other).upper()

    def __ge__(self, other):
        return str(self).upper() >= str(other).upper()

    def __lt__(self, other):
        return str(self).upper() < str(other).upper()

    def __le__(self, other):
        return str(self).upper() <= str(other).upper()

    def __str__(self):
        return str(self.value)
