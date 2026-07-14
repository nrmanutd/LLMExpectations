from abc import ABC, abstractmethod
from datetime import date


class BaseSurveySerializer(ABC):
    @abstractmethod
    def saveSurvey(self, survey, surveyDate: date):
        pass