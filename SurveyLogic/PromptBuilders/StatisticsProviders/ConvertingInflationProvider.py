import re
from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseInflationProvider import BaseInflationProvider


class ConvertingInflationProvider(BaseInflationProvider):
    def __init__(self, provider: BaseInflationProvider, regionMapPath: Path, productMapPath: Path):
        self.provider = provider
        self.regionMap = self._getRegionMap(regionMapPath)

    def getProductsRegionalYearInflationLastNMonth(self, d: date, region: str, products: list[str],
                                                   lastMonth: int = 1) -> list[float]:


        r = self.regionMap[region]
        return self.provider.getProductsRegionalYearInflationLastNMonth(d, r, products, lastMonth)

    def getProductsCommonYearInflationLastNMonth(self, d: date, products: list[str], lastMonth: int = 1) -> list[
        float]:

        return self.provider.getProductsCommonYearInflationLastNMonth(d, products, lastMonth)

    def getAverageRegionalYearInflationLastNMonth(self, d: date, region: str, lastMonth: int = 1) -> float:
        r = self.regionMap[region]
        return self.provider.getAverageRegionalYearInflationLastNMonth(d, r, lastMonth)

    def getAverageCommonYearInflationLastNMonth(self, d: date, lastMonth: int = 1) -> float:
        return self.provider.getAverageCommonYearInflationLastNMonth(d, lastMonth)

    def _getRegionMap(self, path: Path) -> dict:
        mm = dict()

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for l in lines:
                pattern = r'(\d{1,2})\s*(.*);(.*)$'
                m = re.match(pattern, l.strip())

                number, rlms, infl = m.groups()
                mm[number] = infl

        return mm
