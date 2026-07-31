from abc import ABC, abstractmethod
from datetime import date


class BaseAverageExpensesProvider(ABC):
    @abstractmethod

    def getRegionAverageExpenses(self, region: str, d: date) -> float:
        pass