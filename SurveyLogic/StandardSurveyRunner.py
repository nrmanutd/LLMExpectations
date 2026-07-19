from datetime import date

from Logging.BaseLogger import BaseLogger
from SurveyLogic.BaseSurveyRunner import BaseSurveyRunner
from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider
from SurveyLogic.SurveyExecution.BaseSurveyExecutor import BaseSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer


class StandardSurveyRunner(BaseSurveyRunner):
    def __init__(self, serializer: BaseSurveySerializer, surveyExecutor: BaseSurveyExecutor, profilesProvider: BaseProfilesProvider, logger: BaseLogger):
        self.logger = logger
        self.surveyExecutor = surveyExecutor
        self.serializer = serializer
        self.profilesProvider = profilesProvider

    def RunSurvey(self, surveyDate: date):
        result = []

        profiles = self.profilesProvider.getProfiles(surveyDate)

        for i in range(len(profiles)):
            p = profiles[i]
            self.logger.logDebug(f'Executing survey for profile #{i} (of {len(profiles)}): {p}...')
            r = self.surveyExecutor.executeSurvey(surveyDate, p)
            self.logger.logDebug(f'Surveyed profile # {i}.')
            result.append(r)

            self.serializer.saveSurvey(result, surveyDate)
            self.logger.logDebug(f'Saved survey.')

        return result
