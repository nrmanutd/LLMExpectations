from abc import ABC, abstractmethod
from datetime import date


class BaseWeeklyInflationProvider(ABC):
    @abstractmethod
    def getWeeklyInflation(self, d: date, products: list[str], weeksOffset: int) -> list[float]:
        pass
