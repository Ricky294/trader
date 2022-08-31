import random


def char_sequence(start: int, end: int):
    """

    >>> list(char_sequence(65, 70))
    ['A', 'B', 'C', 'D', 'E']
    """

    return (chr(i) for i in range(start, end))


def random_string(char_set: str, length: int):
    """Creates a random string with the defined `length`
    by randomly selecting characters from `char_set`.

    :example:
    >>> random.seed(1)
    >>> random_string('ABX', length=5)
    'AXABA'
    """
    return ''.join(random.choice(char_set) for _ in range(length))

