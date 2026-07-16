from datetime import date

from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class FixedProfilesProvider(BaseProfilesProvider):
    def __init__(self, profiles: list[ProfileData]):
        self.profiles = profiles

    def getProfiles(self, surveyDate: date):
        return self.profiles
