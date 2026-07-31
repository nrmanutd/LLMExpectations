import re
from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseAverageExpensesProvider import BaseAverageExpensesProvider


class ConvertingAverageExpensesProvider(BaseAverageExpensesProvider):
    def __init__(self, provider: BaseAverageExpensesProvider, path: Path):
        self.provider = provider
        self.regionsMap = self._getRegionsMap(path)
    def getRegionAverageExpenses(self, region: str, d: date) -> float:
        r = self.regionsMap[region]
        return self.provider.getRegionAverageExpenses(r, d)

    def _getRegionsMap(self, path: Path):
        mm = dict()

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for l in lines:
                pattern = r'(\d{1,2})\s*(.*);(.*)$'
                m = re.match(pattern, l.strip())

                number, rlms, infl = m.groups()

                mm[number] = infl

        print(mm)
        return mm