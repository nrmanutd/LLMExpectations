from abc import ABC, abstractmethod
from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class BaseSurveyRunner(ABC):
    @abstractmethod
    def RunSurvey(self, surveyDate: date, profiles: list[ProfileData]):
        pass