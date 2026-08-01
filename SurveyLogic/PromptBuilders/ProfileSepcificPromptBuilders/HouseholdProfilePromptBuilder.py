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

        mortgageDescription = self._getMortgageDescription(profile)
        prompt = prompt.replace(constants.mortgageInformation, mortgageDescription)

        sameRespondent = self._getSameRespondentInformation(profile)
        prompt = prompt.replace(constants.individualAndHouseholdRespndent, sameRespondent)

        creditDebt = self._getCreditDebt(profile)
        prompt = prompt.replace(constants.creditDebt, creditDebt)

        carsDescription = self._getCarsDescription(profile)
        prompt = prompt.replace(constants.householdCars, carsDescription)

        return prompt

    def _getSameRespondentInformation(self, profile: ProfileData):
        if profile.idIndividualrespondent == profile.idHHrespondent:
            return 'тот же самый, что и дает ответы на вопрос анкеты о домохозяйтсве'

        return 'другой член домохозяйства давал ответы на вопросы анкеты о домохозястве'
    def _getExpensesRepresentation(self, profile: ProfileData, expenses: float):
        if self._checkNoAnswer(profile.allFamilyMonthIncome):
            return self._getNoAnswerDescription(profile.allFamilyMonthIncome)

        ratio = profile.allFamilyMonthIncome / (expenses * profile.totalFamilyMembers / 12)
        return f'{ratio: .1f} в регионе {profile.currentLocalityRegion}'

    def _getMortgageDescription(self, profile):
        baseInformation = f'Тип жилья - {profile.familyHouseType}, семья занимает {profile.familyHouseAllocationType}, общая площадь - {profile.familyHouseTotalSquare}'
        countryInformation = f'Есть дача: {profile.hasCountryHouse}, есть иная недвижимость: {profile.hasOtherMortgage}'
        landInformation = f'Семья пользуется землей: {profile.hasLand}, собственность: {profile.landOwner}'

        return f'\n{baseInformation}\n{countryInformation}\n{landInformation}.'

    def _getCreditDebt(self, profile):
        if profile.familyHasActiveCredits == 'Нет':
            return 'у домохозяйства нет активных кредитов.'

        if self._checkNoAnswer(profile.totalFamilyCreditDebt):
            return self._getNoAnswerDescription(profile.totalFamilyCreditDebt)

        ratio = profile.totalFamilyCreditDebt / (profile.allFamilyMonthIncome * 12)

        return f'Совокупная задолженность домохозяйства по всем кредитам эквивалентна {ratio: .1f} годам работы семьи при условии, что все заработанные деньги будут уходить на погашение кредита.'

    def _checkNoAnswer(self, value):
        noAnswerSet = {99999997, 99999998, 99999999}
        if value in noAnswerSet or value is None:
            return True

        return False

    def _getNoAnswerDescription(self, value):
        if value == 99999997:
            return 'затрудняюсь ответить'
        elif value == 99999998:
            return 'отказ от ответа'
        elif value == 99999999:
            return 'нет ответа'
        elif value is None:
            return 'нет информации'

        raise ValueError(f'Incorrect value: {value}')

    def _getCarsDescription(self, profile):
        domesticCar = f'отечественный автомобиль {'имеется' if profile.hasRussianCar == 'Да' else 'отсутствует'}'
        foreignCar = f'иностранный автомобиль {'имеется' if profile.hasForeignCar == 'Да' else 'отсутствует'}'

        return f'{domesticCar}, {foreignCar}.'

