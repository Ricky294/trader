from __future__ import annotations

import requests
import json


class FearAndGreed:

    def __init__(self, timestamp: int | str, value: int | str, level: str):
        self.timestamp = int(timestamp)
        self.value = int(value)
        self.level = level

    def __str__(self):
        return str(self.__dict__)


def get_fear_and_greed(n=1):
    """
    Returns a list of dict with fear and greed data.

    Each dict contains the following keys: ['value', 'value_classification', 'timestamp']

    :param n: Size of the returned list.
    :return: list of FearAndGreed objects
    """

    response = requests.get(f'https://api.alternative.me/fng/?limit={n}')

    content = response.content

    list_of_dict = json.loads(content)['data']

    ret = [
        FearAndGreed(timestamp=dct['timestamp'], value=dct['value'], level=dct['value_classification'])
        for dct in list_of_dict
    ]

    return ret
