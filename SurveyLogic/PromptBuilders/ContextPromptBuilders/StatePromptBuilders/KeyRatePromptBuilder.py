from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseKeyRateProvider import BaseKeyRateProvider
from SurveyLogic.PromptBuilders.commonHelpers import getDescriptionRate


class KeyRatePromptBuilder(BasePromptBuilder):
    def __init__(self, keyRateProvider: BaseKeyRateProvider):
        self.keyRateProvider = keyRateProvider

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        keyRates = self.keyRateProvider.getKeyRateIncrements(surveyDate, 3)

        tt = ['последнем', 'предыдущем', 'предпредыдущем']

        result = ''
        for i in range(len(keyRates)):
            desc = getDescriptionRate(keyRates[i])
            result += f'На {tt[i]} заседании ЦБ {desc}.\n'

        if result == '':
            return 'Нет информации'

        return result