from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseInflationProvider import \
    BaseInflationProvider
from SurveyLogic.PromptBuilders.commonHelpers import loadRlmsGoodsToRosstatGoodsMap, getTop5, \
    getDescriptionMonth


class ExpensesProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, promptTemplate: str, provider: BaseInflationProvider, pathes: list[Path]):
        self.prompt = promptTemplate
        self.inflationProvider = provider

        self.map = loadRlmsGoodsToRosstatGoodsMap(pathes)

    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        goods = [profile.regular, profile.durable, profile.services]
        goodNames = [constants.regularTag, constants.durableTag, constants.servicesTag]
        goodsStatus = [True, True, True]

        result = self.prompt
        for i in range(len(goods)):
            top5Goods = getTop5(self.map, goods[i])

            inflation1m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 1)
            inflation3m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 3)
            inflation6m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 6)

            currentPrompt = self._getCurrentGoodsPromptSet(top5Goods, inflation1m, inflation3m, inflation6m)
            if 'нет информации' in currentPrompt:
                goodsStatus[i] = False

            result = result.replace(goodNames[i], currentPrompt)

        if not any(goodsStatus):
            return None

        return result

    def _getCurrentGoodsPromptSet(self, top5Goods: list[str], inflation1m: list[float], inflation3m: list[float], inflation6m: list[float]) -> str:
        result = '\n'

        for i in range(len(top5Goods)):
            inflation1mDescription = getDescriptionMonth(inflation1m[i], 1)
            inflation3mDescription = getDescriptionMonth(inflation3m[i], 3)
            inflation6mDescription = getDescriptionMonth(inflation6m[i], 6)
            inflation12mDescription = getDescriptionMonth(inflation6m[i], 12)

            curDescription = ''
            if 'нет информации' not in inflation1mDescription:
                curDescription += f' {inflation1mDescription},'

            if 'нет информации' not in inflation3mDescription:
                curDescription += f' {inflation3mDescription},'

            if 'нет информации' not in inflation6mDescription:
                curDescription += f' {inflation6mDescription},'

            if 'нет информации' not in inflation12mDescription:
                curDescription += f' {inflation12mDescription}'

            if curDescription == '':
                continue

            result += f'#{i}. {top5Goods[i]}:{curDescription}\n'

        if result == '\n':
            return 'нет информации'

        return result




