from abc import ABC, abstractmethod
from datetime import date


class BaseSurveyer(ABC):
    @abstractmethod
    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str, surveyDate: date):
        pass