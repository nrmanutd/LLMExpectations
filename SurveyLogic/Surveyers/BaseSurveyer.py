from abc import ABC, abstractmethod
from datetime import date

from SurveyLogic.SurveyResults.InflationSurveyRespond import InflationSurveyRespond


class BaseSurveyer(ABC):
    @abstractmethod
    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str, surveyDate: date)->InflationSurveyRespond:
        pass