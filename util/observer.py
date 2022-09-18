import abc
from typing import Set


class Observer(abc.ABC):

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        ...


class Subject:

    def __init__(self):
        self._observers: Set[Observer] = set()

    def attach(self, obs: Observer):
        self._observers.add(obs)

    def detach(self, obs: Observer):
        self._observers.remove(obs)

    def notify(self, *args, **kwargs):
        for sub in self._observers:
            sub.update(*args, **kwargs)
