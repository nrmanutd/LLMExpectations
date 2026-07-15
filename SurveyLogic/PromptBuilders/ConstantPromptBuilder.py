from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class ConstantPromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        return self.prompt
