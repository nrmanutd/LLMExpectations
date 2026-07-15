from datetime import date

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.Prompts import prompts


class TaskPromptBuilder(BasePromptBuilder):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        prompt = self.prompt.replace(constants.surveyDateTag, surveyDate.strftime('%d.%m.%Y'))
        prompt = prompt.replace(constants.respondentIdTag, profile.respondentId)
        return prompt