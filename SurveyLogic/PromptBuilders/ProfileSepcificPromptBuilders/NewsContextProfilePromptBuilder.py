from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class NewsContextProfilePromptBuilder(BasePromptBuilder):
    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        pass