from datetime import date

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.constants import surveyDateTag


class SystemPromptBuilder(BasePromptBuilder):
    def __init__(self, systemPromptTemplate: str):
        self.systemPromptTemplate = systemPromptTemplate

    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        resultPrompt = self.systemPromptTemplate.replace(surveyDateTag, surveyDate.strftime('%d.%m.%Y'))
        return resultPrompt