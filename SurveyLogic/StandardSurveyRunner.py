from datetime import date

from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.BaseSurveyRunner import BaseSurveyRunner
from SurveyLogic.SurveyExecution.BaseSurveyExecutor import BaseSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer


class StandardSurveyRunner(BaseSurveyRunner):
    def __init__(self, serializer: BaseSurveySerializer, surveyExecutor: BaseSurveyExecutor, profilesProvider: BaseProfilesProvider):
        self.surveyExecutor = surveyExecutor
        self.serializer = serializer
        self.profilesProvider = profilesProvider

    def RunSurvey(self, surveyDate: date):
        result = []

        profiles = self.profilesProvider.getProfiles(surveyDate)

        for p in profiles:
            r = self.surveyExecutor.executeSurvey(surveyDate, p)
            result.append(r)

            self.serializer.saveSurvey(result, surveyDate)

        return result
