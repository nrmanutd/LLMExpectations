from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseInflationProvider import BaseInflationProvider
from SurveyLogic.PromptBuilders.commonHelpers import convertToPromptValue


class StateInflationContextPromptBuilder(BasePromptBuilder):
    def __init__(self, promptTemplate: str, provider: BaseInflationProvider):
        self.prompt = promptTemplate
        self.inflationProvider = provider

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        inflation1m = self.inflationProvider.getAverageCommonYearInflationLastNMonth(surveyDate, 1)
        inflation3m = self.inflationProvider.getAverageCommonYearInflationLastNMonth(surveyDate, 3)
        inflation1Y = self.inflationProvider.getAverageCommonYearInflationLastNMonth(surveyDate, 12)

        prompt = self.prompt.replace(constants.inflation1M, convertToPromptValue(inflation1m))
        prompt = prompt.replace(constants.inflation3M, convertToPromptValue(inflation3m))
        prompt = prompt.replace(constants.inflation1Y, convertToPromptValue(inflation1Y))

        return prompt
