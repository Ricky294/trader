import random
import uuid


def generate_uuid4():
    """Generates random UUID4."""
    return str(uuid.uuid4())


def char_sequence(start: int, end: int):
    """

    >>> list(char_sequence(65, 70))
    ['A', 'B', 'C', 'D', 'E']

    >>> list(char_sequence(70, 65))
    ['F', 'E', 'D', 'C', 'B']
    """

    if start < end:
        it = range(start, end)
    else:
        it = range(start, end, -1)

    return (chr(i) for i in it)


def random_string(char_set: str, length: int):
    """Creates a random string with the defined `length`
    by randomly selecting characters from `char_set`.

    :example:
    >>> random.seed(1)
    >>> random_string('ABX', length=5)
    'AXABA'
    """
    return ''.join(random.choice(char_set) for _ in range(length))


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
