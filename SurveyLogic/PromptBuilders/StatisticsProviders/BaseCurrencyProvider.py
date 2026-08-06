from abc import ABC, abstractmethod
from datetime import date


class BaseCurrencyProvider(ABC):
    @abstractmethod
    def getRateDifferenceByDaysOffset(self, d: date, offset: int):
        pass

    @abstractmethod
    def getRateDifferenceByWeeksOffset(self, d: date, offset: int):
        pass

    @abstractmethod
    def getRateDifferenceByMonthOffset(self, d: date, offset: int):
        pass