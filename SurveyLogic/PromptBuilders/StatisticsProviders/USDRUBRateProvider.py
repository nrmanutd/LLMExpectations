from datetime import date

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseCurrencyProvider import BaseCurrencyProvider


class USDRUBRateProvider(BaseCurrencyProvider):
    def getRateDifferenceByMonthOffset(self, d: date, offset: int):
        pass

    def getRateDifferenceByWeeksOffset(self, d: date, offset: int):
        pass

    def getRateDifferenceByDaysOffset(self, d: date, offset: int):
        pass