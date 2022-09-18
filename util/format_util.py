"""Implements core utility functions for string and number formatting.

Functions:
    - num - Formats number parameter with defined precision, percentage or plus sign.
"""
import json
from typing import Any

from util.inspect_util import is_iterable, is_bool, is_number, is_int


def normalize_data_types(dct: dict[str, Any]) -> dict[str, Any]:
    """
    Converts the data types of string values in a dictionary to the appropriate type.

    This function iterates through the keys and values in the input dictionary and attempts to
    convert string values to the appropriate data type (int, float, or bool). If a value cannot
    be converted, it is left as a string.

    Args:
        dct (dict[str, Any]): The input dictionary.

    Returns:
        dict[str, Any]: A new dictionary with the fixed data types.

    Examples:
        >>> normalize_data_types({'a': '1', 'b': '2.5', 'c': 'true', 'd': 'abc'})
        {'a': 1, 'b': 2.5, 'c': True, 'd': 'abc'}
        >>> normalize_data_types({'a': '1', 'b': '2.5', 'c': 'false', 'd': 'abc'})
        {'a': 1, 'b': 2.5, 'c': False, 'd': 'abc'}
        >>> normalize_data_types({'a': 1, 'b': 2.5, 'c': True, 'd': 'abc'})
        {'a': 1, 'b': 2.5, 'c': True, 'd': 'abc'}
    """

    def generate():
        for key, val in dct.items():
            if isinstance(val, str):
                if is_int(val):
                    yield key, int(val)
                elif is_number(val):
                    yield key, float(val)
                elif is_bool(val):
                    yield key, True if val.lower() == 'true' else False
                else:
                    yield key, val
            else:
                yield key, val

    return dict(generate())


def concat_params(*args, **kwargs) -> str:
    """
    Concatenates arguments and keyword arguments by ', '.

    Examples

    >>> concat_params()
    ''

    >>> concat_params('val1', 'val2')
    'val1, val2'

    >>> concat_params(kwarg1=1, kwarg2=2)
    'kwarg1=1, kwarg2=2'

    >>> concat_params('val1', 'val2', kwarg1=1, kwarg2=2)
    'val1, val2, kwarg1=1, kwarg2=2'
    """

    concat_args = ', '.join(str(arg) for arg in args)
    concat_kwargs = ', '.join(key + '=' + str(val) for key, val in kwargs.items())

    if concat_args and concat_kwargs:
        return ', '.join((concat_args, concat_kwargs))
    elif concat_args:
        return concat_args
    return concat_kwargs


def num(inp, /, prec=0, perc=False, plus=False):
    """
    Number formats parameter `x`.

    :param inp: Input number(s).
    :param prec: Defines the number of fixed precision points.
    :param perc: If True, postfixes the number with a '%' sign and multiplies it by 100.
    :param plus: If True, prefixes the number with a '+' sign when number is positive or 0.

    :return: Formatted number.

    Usage examples
    --------------
    >>> num(10)
    '10'

    >>> num([10, 10, 10, None])
    ['10', '10', '10', None]

    >>> num(-12345.56789, prec=3, plus=True)
    '-12,345.568'

    >>> num(3.1415, prec=4, plus=True)
    '+3.1415'

    >>> num(100.12, prec=4, perc=True, plus=True)
    '+10,012.0000%'
    """

    def fmt(val):
        try:
            val = float(val)
        except TypeError:
            return val

        if perc:
            val *= 100
            end = '%'
        else:
            end = ''

        if '.' in str(val):
            ret = '+,.' if plus else ',.'
            return f'{val:{ret}{prec}f}{end}'

        ret = '+,' if plus else ','
        return f'{val:{ret}}{end}'

    return [fmt(e) for e in inp] if is_iterable(inp) else fmt(inp)


def capitalize(var1, var2='', /):
    var1 = str(var1).replace('_', ' ').capitalize()
    if var2:
        return f'{var1} ({var2})'
    return var1


def title(var1, var2='', /):
    var1 = str(var1).replace('_', ' ').title()
    if var2:
        return f'{var1} ({var2})'
    return var1


def upper(var1, var2='', /):
    var1 = str(var1).replace('_', ' ').upper()
    if var2:
        return f'{var1} ({var2})'
    return var1


def camelCase(arg: str) -> str:
    """Converts snake_case input string to camelCase.

    Examples:

    >>> camelCase('hi')
    'hi'

    >>> camelCase('hello_there')
    'helloThere'

    >>> camelCase('HELLO_THERE')
    'helloThere'
    """

    splits = arg.split('_')
    first_split = splits.pop(0).lower()
    return first_split + ''.join([split.lower().title() for split in splits])


def snake_case(key: str) -> str:
    """
    Converts string to snake case.

    Examples:
        >>> snake_case('HelloThere')
        'hello_there'
    """
    import re
    return re.sub(r'([A-Z])', r'_\1', key).lower().strip('_')


def round_down(number: float, precision: int) -> float:
    """
    Rounds down the `number` by a number of `precision` points (truncates value).

    :examples:
    >>> round_down(1, precision=2)
    1.0

    >>> round_down(1.1, precision=1)
    1.1

    >>> round_down(1.9999, precision=2)
    1.99
    """

    s = str(number)
    if '.' not in s:
        return float(number)

    return float(s[: s.find('.') + precision + 1])


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
