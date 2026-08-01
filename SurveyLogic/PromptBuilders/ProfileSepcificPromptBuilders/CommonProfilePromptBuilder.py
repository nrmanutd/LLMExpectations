from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.StatisticsProviders.BaseAverageExpensesProvider import BaseAverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider


class CommonProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str, mrotProvider: MROTProvider, averageExpensesProvider: BaseAverageExpensesProvider):
        self.averageExpensesProvider = averageExpensesProvider
        self.mrotProvider = mrotProvider
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        prompt = self.prompt.replace(constants.surveyDateTag, self._getMonth(surveyDate.month))
        prompt = prompt.replace(constants.ageTag, str(profile.age))
        prompt = prompt.replace(constants.sexTag, str(profile.sex))
        prompt = prompt.replace(constants.localityTag, str(profile.currentLocality))
        prompt = prompt.replace(constants.localityTypeTag, str(profile.typeOfLocality))
        prompt = prompt.replace(constants.educationTag, str(profile.education))
        prompt = prompt.replace(constants.nationalityTag, str(profile.nationality))
        prompt = prompt.replace(constants.familyStatusTag, str(profile.familyStatus))
        prompt = prompt.replace(constants.currentStatusTag, str(profile.currentStatus))
        prompt = prompt.replace(constants.jobSectorTag, str(profile.jobSector))
        prompt = prompt.replace(constants.jobTag, str(profile.job))

        salary = self._processSalary(surveyDate, profile)

        prompt = prompt.replace(constants.salaryTag, salary)
        prompt = prompt.replace(constants.economicsSourceOfKnowledge, str(profile.economicsSourceOfKnowledge))
        prompt = prompt.replace(constants.hasSavingsTag, "Да" if profile.hasSavings else "Нет")
        prompt = prompt.replace(constants.hasCreditsTag, "Да" if profile.hasCredit else "Нет")

        return prompt

    def _getMonth(self, month: int):
        months = {
            1: 'январь', 2: 'февраль', 3: 'март', 4: 'апрель',
            5: 'май', 6: 'июнь', 7: 'июль', 8: 'август',
            9: 'сентябрь', 10: 'октябрь', 11: 'ноябрь', 12: 'декабрь'
        }

        return months[month]

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

