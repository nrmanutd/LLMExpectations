from abc import ABC, abstractmethod
from datetime import date


class BaseSingleMonthInflationProvider(ABC):
    @abstractmethod
    def getInflation(self, region: str, product: str, d: date):
        pass