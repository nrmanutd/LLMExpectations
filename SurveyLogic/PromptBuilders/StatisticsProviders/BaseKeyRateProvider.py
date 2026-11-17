from abc import ABC, abstractmethod
from datetime import date


class BaseKeyRateProvider(ABC):
    @abstractmethod
    def getKeyRateIncrements(self, d:date, lastN:int = 1) -> list[float]:
        pass