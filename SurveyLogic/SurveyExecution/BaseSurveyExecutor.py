from abc import ABC, abstractmethod
from datetime import date
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class BaseSurveyExecutor(ABC):
    @abstractmethod
    def executeSurvey(self, surveyDate: date, profile: ProfileData):
        pass