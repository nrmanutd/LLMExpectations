from datetime import date

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider


class DateRoundingSingleMonthInflationProvider(BaseSingleMonthInflationProvider):
    def __init__(self, provider: BaseSingleMonthInflationProvider):
        self.provider = provider

    def getInflation(self, region: str, product: str, d: date):
        newDate = date(year=d.year, month=d.month, day=1)
        return self.provider.getInflation(region, product, newDate)
