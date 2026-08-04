from abc import ABC, abstractmethod
from datetime import datetime, date


class BaseInflationProvider(ABC):
    @abstractmethod
    def getAverageCommonYearInflationLastNMonth(self, d: date, lastMonth: int = 1) -> float:
        pass

    @abstractmethod
    def getAverageRegionalYearInflationLastNMonth(self, d: date, region: str, lastMonth: int = 1) -> float:
        pass

    @abstractmethod
    def getProductsCommonYearInflationLastNMonth(self, d: date, products: list[str], lastMonth: int = 1) -> list[
        float]:
        pass

    @abstractmethod
    def getProductsRegionalYearInflationLastNMonth(self, d: date, region: str, products: list[str],
                                                   lastMonth: int = 1) -> list[float]:
        pass