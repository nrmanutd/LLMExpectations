from abc import ABC
from datetime import datetime


class InflationProvider(ABC):
    def getAverageCommonYearInflationLastNMonth(self, date: datetime, lastMonth: int = 1) -> float:
        pass

    def getAverageRegionalYearInflationLastNMonth(self, date: datetime, region: str, lastMonth: int = 1) -> float:
        pass

    def getProductsCommonYearInflationLastNMonth(self, date: datetime, products: list[str], lastMonth: int = 1) -> list[float]:
        pass

    def getProductsRegionalYearInflationLastNMonth(self, date: datetime, region: str, products: list[str], lastMonth: int = 1) -> list[float]:
        pass
