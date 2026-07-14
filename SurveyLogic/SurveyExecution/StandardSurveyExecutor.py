from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.SurveyExecution.BaseSurveyExecutor import BaseSurveyExecutor
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


class StandardSurveyExecutor(BaseSurveyExecutor):
    def __init__(self, promptBuilder: BasePromptBuilder, surveyer: BaseSurveyer):
        self.surveyer = surveyer
        self.promptBuilder = promptBuilder

    def executeSurvey(self, surveyDate: date, profile: ProfileData):
        prompt = self.promptBuilder.buildPrompt(surveyDate, profile)
        respond = self.surveyer.askSurvey(prompt)

        return respond