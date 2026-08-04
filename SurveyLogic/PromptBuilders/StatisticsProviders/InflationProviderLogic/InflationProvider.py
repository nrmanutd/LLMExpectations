import re
from datetime import date
from pathlib import Path

import pandas as pd

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseInflationProvider import BaseInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider


class InflationProvider(BaseInflationProvider):
    def __init__(self, singleMonthInflationProvider: BaseSingleMonthInflationProvider):
        self.singleMonthInflationProvider = singleMonthInflationProvider

    def getAverageCommonYearInflationLastNMonth(self, d: date, lastMonth: int = 1) -> float:
        return self.getAverageRegionalYearInflationLastNMonth(d, 'Российская Федерация', lastMonth)

    def getAverageRegionalYearInflationLastNMonth(self, d: date, region: str, lastMonth: int = 1) -> float:
        allGoodsInflation = self.getProductsRegionalYearInflationLastNMonth(d, region, ['Все товары и услуги'], lastMonth)
        return allGoodsInflation[0]

    def getProductsCommonYearInflationLastNMonth(self, d: date, products: list[str], lastMonth: int = 1) -> list[float]:
        return self.getProductsRegionalYearInflationLastNMonth(d, 'Российская Федерация', products, lastMonth)

    def getProductsRegionalYearInflationLastNMonth(self, d: date, region: str, products: list[str], lastMonth: int = 1) -> list[float]:
        resultInflation = []

        for p in products:
            inflation = self._getInflation(d, region, p, lastMonth)
            resultInflation.append(inflation)

        return resultInflation

    def _getInflation(self, d: date, region: str, product: str, lastMonth: int = 1):
        columns = []

        inflation = 1
        for i in range(lastMonth):
            dateWithOffset = (d - pd.DateOffset(months=i + 1)).date()
            currentInflation = self.singleMonthInflationProvider.getInflation(region, product, dateWithOffset)

            if currentInflation is None:
                return None

            inflation = inflation * currentInflation / 100

        yearInflation = inflation ** (12 / lastMonth) - 1
        return yearInflation
