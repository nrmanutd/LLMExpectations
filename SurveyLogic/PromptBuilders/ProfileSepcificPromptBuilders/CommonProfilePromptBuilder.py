from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseAverageExpensesProvider import BaseAverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider
from SurveyLogic.PromptBuilders.commonHelpers import months_ru


class CommonProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str, mrotProvider: MROTProvider, averageExpensesProvider: BaseAverageExpensesProvider):
        self.averageExpensesProvider = averageExpensesProvider
        self.mrotProvider = mrotProvider
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        prompt = self.prompt.replace(constants.surveyDateTag, months_ru[surveyDate.month])
        prompt = prompt.replace(constants.ageTag, self._processIfNone(profile.age))
        prompt = prompt.replace(constants.sexTag, self._processIfNone(profile.sex))
        prompt = prompt.replace(constants.localityTag, self._processIfNone(profile.currentLocality))
        prompt = prompt.replace(constants.localityTypeTag, self._processIfNone(profile.typeOfLocality))
        prompt = prompt.replace(constants.educationTag, self._processIfNone(profile.education))
        prompt = prompt.replace(constants.nationalityTag, self._processIfNone(profile.nationality))
        prompt = prompt.replace(constants.familyStatusTag, self._processIfNone(profile.familyStatus))
        prompt = prompt.replace(constants.currentStatusTag, self._processIfNone(profile.currentStatus))
        prompt = prompt.replace(constants.jobSectorTag, self._processIfNone(profile.jobSector))
        prompt = prompt.replace(constants.jobTag, self._processIfNone(profile.job))

        salary = self._processSalary(surveyDate, profile)

        prompt = prompt.replace(constants.salaryTag, salary)
        prompt = prompt.replace(constants.economicsSourceOfKnowledge, self._processIfNone(profile.economicsSourceOfKnowledge))
        prompt = prompt.replace(constants.hasSavingsTag, "Да" if profile.hasSavings else "Нет")
        prompt = prompt.replace(constants.hasCreditsTag, "Да" if profile.hasCredit else "Нет")

        return prompt

    def _processIfNone(self, data):
        if data is None or data == 'None':
            return 'Нет информации'

        return str(data)

    def _processSalary(self, surveyDate: date, profile: ProfileData) -> str:
        if profile.salary is None or profile.salary == '':
            return 'Нет ответа'
        elif '99999998' in profile.salary:
            return 'Отказ от ответа'
        elif '99999997' in profile.salary:
            return 'Затрудняюсь ответить'
        elif '99999999' in profile.salary:
            return 'Нет ответа'

        s = float(profile.salary)
        mrot = self.mrotProvider.getMROT(surveyDate)
        averageExpenses = self.averageExpensesProvider.getRegionAverageExpenses(profile.currentLocalityRegionCode, surveyDate)/12

        salaryInMrot = s / mrot
        salaryInAverages = s / averageExpenses

        salary = f'{salaryInMrot: .1f} в терминах МРОТ (по всей России), {salaryInAverages: .1f} в терминах средних трат по региону проживания {profile.currentLocalityRegion}'
        return salary

