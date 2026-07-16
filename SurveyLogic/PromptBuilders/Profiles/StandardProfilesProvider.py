from datetime import date

from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider


class StandardProfilesProvider(BaseProfilesProvider):
    def getProfiles(self, surveyDate: date):

        raise NotImplementedError('Method not implemented')