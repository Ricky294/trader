"""Implements core utility functions for string and number formatting.

Functions:
    - num - Formats number parameter with defined precision, percentage or plus sign.
"""

from util.inspect_util import is_iterable


def num(inp, /, prec=0, perc=False, plus=False):
    """
    Number formats parameter `x`.

    :param inp: Input number(s).
    :param prec: Defines the number of fixed precision points.
    :param perc: If True, postfixes the number with a '%' sign and multiplies it by 100.
    :param plus: If True, prefixes the number with a '+' sign when number is positive or 0.

    :return: Formatted number.

    :examples:
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
        return f"{var1} ({var2})"
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


def round_down(number: float | None, precision: int):
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

    if number is None:
        return

    s = str(number)
    if '.' not in s:
        return float(number)

    return float(s[: s.find('.') + precision + 1])
