from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseInflationProvider import BaseInflationProvider
from SurveyLogic.PromptBuilders.commonHelpers import loadRlmsGoodsToRosstatGoodsMap, showInflation


class ExpensesProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, promptTemplate: str, provider: BaseInflationProvider, pathes: list[Path]):
        self.prompt = promptTemplate
        self.inflationProvider = provider

        self.map = loadRlmsGoodsToRosstatGoodsMap(pathes)
    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        goods = [profile.regular, profile.durable, profile.services]
        goodNames = [constants.regularTag, constants.durableTag, constants.servicesTag]

        result = self.prompt
        for i in range(len(goods)):
            top5Goods = self._getTop5(goods[i])

            inflation1m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 1)
            inflation3m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 3)
            inflation6m = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(surveyDate, profile.currentLocalityRegionCode, top5Goods, 6)

            currentPrompt = self._getCurrentGoodsPromptSet(top5Goods, inflation1m, inflation3m, inflation6m)
            result = result.replace(goodNames[i], currentPrompt)

        return result

    def _getTop5(self, goods: dict[str, float]):
        rosstatGoods = dict[str, float]()

        for k, v in goods.items():
            g = self.map[k]
            if g == ('нет соответствующей категории'):
                continue

            if g in rosstatGoods:
                rosstatGoods[g] += v
            else:
                rosstatGoods[g] = v

        top_5 = sorted(rosstatGoods.items(), key=lambda x: x[1], reverse=True)[:min(5, len(rosstatGoods))]
        return [item[0] for item in top_5]

    def _getCurrentGoodsPromptSet(self, top5Goods: list[str], inflation1m: list[float], inflation3m: list[float], inflation6m: list[float]) -> str:
        result = '\n'

        for i in range(len(top5Goods)):
            inflation1mDescription = self._getDescription(inflation1m[i], 1)
            inflation3mDescription = self._getDescription(inflation3m[i], 3)
            inflation6mDescription = self._getDescription(inflation6m[i], 6)

            result += f'#{i}. {top5Goods[i]}: {inflation1mDescription}, {inflation3mDescription}, {inflation6mDescription}\n'

        return result

    def _getDescription(self, inflation: float, month: int):
        direction = self._getDirection(inflation)
        if abs(inflation) < 0.00001:
            return f"за последние {month} месяцев не изменилась"

        clearInflation = (inflation + 1)**(month/12) - 1
        return f'{direction} на {showInflation(abs(clearInflation))}% за последние {month} месяцев'

    def _getDirection(self, inflation: float):
        if inflation > 0.0:
            return "подорожал"

        if inflation < 0.0:
            return "подешевел"

        return "цена не изменилась"


