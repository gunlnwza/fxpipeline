from abc import ABC, abstractmethod


class Strategy(ABC):
    @abstractmethod
    def act(self, sim):
        pass
