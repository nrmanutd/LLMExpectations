from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder


class StandardPromptBuilder(BasePromptBuilder):
    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        pass