import random
from datetime import date

from SurveyLogic.PromptBuilders.Profiles.BaseProfilesProvider import BaseProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class RandomSubsampleProfilesProvider(BaseProfilesProvider):
    def __init__(self, profiles: list[ProfileData], alpha: float):
        self.alpha = alpha
        self.profiles = profiles

        if alpha < 0 or alpha > 1:
            raise ValueError(f'Value of alpha should be 0 <= x <= 1, instead: {alpha}')

    def getProfiles(self, surveyDate: date):
        n = len(self.profiles)
        k = int(self.alpha * n)

        k = max(1, min(k, n))

        return random.sample(self.profiles, k)