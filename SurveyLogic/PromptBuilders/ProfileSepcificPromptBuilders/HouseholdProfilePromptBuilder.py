from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseAverageExpensesProvider import BaseAverageExpensesProvider


class HouseholdProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str, provider: BaseAverageExpensesProvider):
        self.prompt = prompt
        self.provider = provider

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        hhAverageExpenses = self.provider.getRegionAverageExpenses(profile.currentLocalityRegionCode, surveyDate)

        expensesRepresentation = self._getExpensesRepresentation(profile, hhAverageExpenses)
        prompt = self.prompt.replace(constants.familyTotalMonthExpenses, expensesRepresentation)
        prompt = prompt.replace(constants.familyTotalMembers, str(profile.totalFamilyMembers))

        return prompt

    def _getExpensesRepresentation(self, profile: ProfileData, expenses: float):
        if profile.allFamilyMonthIncome == 99999997:
            return 'затрудняюсь ответить'
        elif profile.allFamilyMonthIncome == 99999998:
            return 'отказ от ответа'
        elif profile.allFamilyMonthIncome == 99999999:
            return 'нет ответа'
        elif profile.allFamilyMonthIncome is None:
            return 'нет информации'

        ratio = profile.allFamilyMonthIncome / (expenses * profile.totalFamilyMembers / 12)
        return f'{ratio: .1f} в регионе {profile.currentLocalityRegion}'