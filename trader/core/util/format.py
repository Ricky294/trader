"""Implements core utility functions for string and number formatting.

Functions:
    - num - Formats number parameter with defined precision, percentage or plus sign.
"""


def num(x, /, prec=0, *, perc=False, plus=False):
    """
    Number formats parameter `x`.

    :param x: Input number.
    :param prec: Defines the number of fixed precision points.
    :param perc: If True, postfixes the number with a '%' sign and multiplies it by 100.
    :param plus: If True, prefixes the number with a '+' sign when number is positive or 0.

    :return: Formatted number.

    :examples:
    >>> num(10)
    '10'
    >>> num(-12345.56789, prec=3, plus=True)
    '-12,345.568'
    >>> num(3.1415, prec=4, plus=True)
    '+3.1415'
    >>> num(100.12, prec=4, perc=True, plus=True)
    '+10,012.0000%'
    """
    x = float(x)

    if perc:
        x *= 100
        end = "%"
    else:
        end = ""

    if "." in str(x):
        fmt = "+,." if plus else ",."
        return f"{x:{fmt}{prec}f}{end}"

    fmt = "+," if plus else ","
    return f"{x:{fmt}}{end}"


def capitalize(var1, var2="", /):
    var1 = str(var1).replace('_', ' ').capitalize()
    if var2:
        return f"{var1} ({var2})"
    return var1


def title(var1, var2="", /):
    var1 = str(var1).replace('_', ' ').title()
    if var2:
        return f"{var1} ({var2})"
    return var1


def upper(var1, var2="", /):
    var1 = str(var1).replace('_', ' ').upper()
    if var2:
        return f"{var1} ({var2})"
    return var1
