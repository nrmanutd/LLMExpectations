from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseInflationProvider import \
    BaseInflationProvider
from SurveyLogic.PromptBuilders.commonHelpers import getDescriptionWeeks, getDescriptionMonth


class MarkerGoodsInflationPromptBuilder(BasePromptBuilder):
    def __init__(self, inflationProvider: BaseInflationProvider, regularGoods: list[str], durableGoods: list[str], services: list[str]):
        self.services = services
        self.durableGoods = durableGoods
        self.regularGoods = regularGoods

        self.inflationProvider = inflationProvider

    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        regularGoodsDescription = self._getDescription(surveyDate, profile, self.regularGoods)
        durableGoodsDescription = self._getDescription(surveyDate, profile, self.regularGoods, [False, False, True, True, True, True])
        servicesDescription = self._getDescription(surveyDate, profile, self.regularGoods, [False, False, True, True, True, True])

        return f'Инфляция на товары-маркеры регулярного потребления:\n{regularGoodsDescription}\nИнфляция на товары-маркеры длительного потребления:\n{durableGoodsDescription}\nИнфляция на услуги-маркеры:\n{servicesDescription}'

    def _getDescription(self, surveyDate: date, profile: ProfileData, goods: list[str], mask: list[bool] = None):
        if mask is None:
            mask = True * 6

        description = ''
        region = profile.currentLocalityRegionCode

        for good in goods:
            description += f'{good}:'

            inflation1w = self.inflationProvider.getProductsCommonWeeklyInflationLastNWeeks(surveyDate, [good], 1)
            inflation2w = self.inflationProvider.getProductsCommonWeeklyInflationLastNWeeks(surveyDate, [good], 2)

            inflation1m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, region, [good],
                                                                                            1)
            inflation3m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, region, [good],
                                                                                            3)
            inflation6m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, region, [good],
                                                                                            6)
            inflation12m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, region, [good],
                                                                                             12)

            if inflation1w is not None and mask[0]:
                description += f' {getDescriptionWeeks(inflation1w[0], 1)},'

            if inflation2w is not None and mask[1]:
                description += f' {getDescriptionWeeks(inflation2w[0], 2)},'

            if inflation1m is not None and mask[2]:
                description += f' {getDescriptionMonth(inflation1m[0], 1, isInflation=True)},'

            if inflation3m is not None and mask[3]:
                description += f' {getDescriptionMonth(inflation3m[0], 3, isInflation=True)},'

            if inflation6m is not None and mask[4]:
                description += f' {getDescriptionMonth(inflation6m[0], 6, isInflation=True)},'

            if inflation12m is not None and mask[5]:
                description += f' {getDescriptionMonth(inflation12m[0], 12, isInflation=True)}'

            description += '\n'

        return description