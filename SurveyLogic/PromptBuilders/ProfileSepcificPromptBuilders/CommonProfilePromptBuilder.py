from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class CommonProfilePromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):

        prompt = self.prompt.replace(constants.surveyDateTag, surveyDate.strftime('%d.%m.%Y'))
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
        prompt = prompt.replace(constants.salaryTag, f'{str(profile.salary)} рублей в месяц')
        prompt = prompt.replace(constants.economicsSourceOfKnowledge, str(profile.economicsSourceOfKnowledge))
        prompt = prompt.replace(constants.hasSavingsTag, "Да" if profile.hasSavings else "Нет")
        prompt = prompt.replace(constants.hasCreditsTag, "Да" if profile.hasCredit else "Нет")

        return prompt