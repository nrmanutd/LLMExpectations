from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.SurveyExecution.BaseSurveyExecutor import BaseSurveyExecutor


class AdditionalInformationSurveyExecutor(BaseSurveyExecutor):
    def __init__(self, surveyExecutor: BaseSurveyExecutor):
        self.surveyExecutor = surveyExecutor

    def executeSurvey(self, surveyDate: date, profile: ProfileData):
        result = self.surveyExecutor.executeSurvey(surveyDate, profile)

        result.hasCredit = profile.hasCredit
        result.hasSavings = profile.hasSavings

        return result