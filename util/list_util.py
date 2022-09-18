"""Contains list utility functions."""

from typing import Iterable


def remove_elements(lst: list, elements: Iterable, ignore_not_found=True):
    """Removes all `elements` found in `lst`.

    :raises ValueError: If ignore_not_found is False and any element is not found in the list.

    Examples:
    --------
    >>> x = ['a', 'b', 'c']
    >>> remove_elements(x, ['b', 'c', 'e'], ignore_not_found=True)
    >>> x
    ['a']

    >>> remove_elements(x, ['b', 'c', 'e'], ignore_not_found=False)
    Traceback (most recent call last):
    ...
    ValueError: list.remove(x): x not in list
    """

    if ignore_not_found:
        for element in elements:
            try:
                lst.remove(element)
            except ValueError:
                pass
    else:
        for element in elements:
            lst.remove(element)


def remove_all(lst):
    """
    Remove all elements from a list and return them as a new list.

    Parameters:
        lst (list): The list to remove elements from.

    Returns:
        list: A new list containing the removed elements.

    Example:
    -------

    >>> lst = ['a', 'b', 'c']
    >>> removed_elements = remove_all(lst)
    >>> removed_elements
    ['a', 'b', 'c']
    >>> lst
    []

    """
    removed_elements = lst[:]
    del lst[:]
    return removed_elements
