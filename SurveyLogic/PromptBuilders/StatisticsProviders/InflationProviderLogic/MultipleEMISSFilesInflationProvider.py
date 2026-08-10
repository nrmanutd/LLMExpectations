from datetime import date

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider


class MultipleEMISSFilesInflationProvider(BaseSingleMonthInflationProvider):
    def __init__(self, providers: list[BaseSingleMonthInflationProvider], allowedYears: list[set[int]]):
        self.providers = providers
        self.allowedYears = allowedYears

    def getInflation(self, region: str, product: str, d: date):
        currentYear = d.year

        for i in range(len(self.allowedYears)):
            if currentYear in self.allowedYears[i]:
                return self.providers[i].getInflation(region, product, d)

        raise ValueError(f'Date out of range: {d}, allowed years: {[x for x in self.allowedYears]}')