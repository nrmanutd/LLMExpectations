from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.SurveyExecution.BaseSurveyExecutor import BaseSurveyExecutor
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


class StandardSurveyExecutor(BaseSurveyExecutor):
    def __init__(self, systemPromptBuilder: BasePromptBuilder, promptBuilder: BasePromptBuilder, surveyer: BaseSurveyer):
        self.systemPromptBuilder = systemPromptBuilder
        self.surveyer = surveyer
        self.promptBuilder = promptBuilder

    def executeSurvey(self, surveyDate: date, profile: ProfileData):
        systemPrompt = self.systemPromptBuilder.buildPrompt(surveyDate, profile)
        prompt = self.promptBuilder.buildPrompt(surveyDate, profile)

        respond = self.surveyer.askSurvey(systemPrompt, prompt, profile.respondentId, surveyDate)

        return respond