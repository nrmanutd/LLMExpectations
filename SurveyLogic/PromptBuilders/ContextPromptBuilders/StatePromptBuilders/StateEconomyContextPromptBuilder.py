from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseCurrencyProvider import BaseCurrencyProvider
from SurveyLogic.PromptBuilders.commonHelpers import getUsdRubDirection, getDeltaDescription


class StateEconomyContextPromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str, usdRubRateChangeProvider: BaseCurrencyProvider):
        self.usdRubRateChangeProvider = usdRubRateChangeProvider
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        rateChange1d = self.usdRubRateChangeProvider.getRateDifferenceByDaysOffset(surveyDate, 1)
        rateChange1w = self.usdRubRateChangeProvider.getRateDifferenceByWeeksOffset(surveyDate, 1)
        rateChange2w = self.usdRubRateChangeProvider.getRateDifferenceByWeeksOffset(surveyDate, 2)

        curMonthFirstDay = date(year=surveyDate.year, month=surveyDate.month, day=1)
        rateChangePrev1m = self.usdRubRateChangeProvider.getRateDifferenceByMonthOffset(curMonthFirstDay, 1)
        rateChangePrev3m = self.usdRubRateChangeProvider.getRateDifferenceByMonthOffset(curMonthFirstDay, 3)
        rateChangePrev6m = self.usdRubRateChangeProvider.getRateDifferenceByMonthOffset(curMonthFirstDay, 6)

        localDescription = self._getLocalDescription(rateChange1d, rateChange1w, rateChange2w)
        globalDescription = self._getGlobalDescription(surveyDate, rateChangePrev1m, rateChangePrev3m, rateChangePrev6m)

        prompt = self.prompt.replace(constants.localUsdRubTag, localDescription)
        prompt = prompt.replace(constants.globalUsdRubTag, globalDescription)

        return prompt

    def _getLocalDescription(self, rateChange1d, rateChange1w, rateChange2w):
        result = ''

        direction1d = getUsdRubDirection(rateChange1d)
        direction1w = getUsdRubDirection(rateChange1w)
        direction2w = getUsdRubDirection(rateChange2w)

        periods = ['предыдущий день', 'предыдущую неделю', 'предыдущие 2 недели']
        directions = [direction1d, direction1w, direction2w]
        rates = [rateChange1d, rateChange1w, rateChange2w]

        for i in range(len(periods)):
            if directions[i] is None:
                continue

            if directions[i] == 'стабилен':
                result += f'за {periods[i]} не изменился\n'
                continue

            result += f'за {periods[i]} {directions[i]} на {abs(rates[i]*100):.1f}%\n'

        return result

    def _getGlobalDescription(self, d: date, rateChangePrev1m, rateChangePrev3m, rateChangePrev6m):
        result = ''

        direction1m = getUsdRubDirection(rateChangePrev1m)
        direction3m = getUsdRubDirection(rateChangePrev3m)
        direction6m = getUsdRubDirection(rateChangePrev6m)

        onePeriod = getDeltaDescription(d, 1)
        threePeriod = getDeltaDescription(d, 3)
        sixPeriod = getDeltaDescription(d, 6)

        periods = [onePeriod, threePeriod, sixPeriod]
        directions = [direction1m, direction3m, direction6m]
        rates = [rateChangePrev1m, rateChangePrev3m, rateChangePrev6m]

        for i in range(len(periods)):
            if directions[i] is None:
                continue

            if directions[i] == 'стабилен':
                result += f'за {periods[i]} не изменился\n'
                continue

            result += f'за {periods[i]} {directions[i]} на {abs(rates[i] * 100):.1f}%\n'

        return result