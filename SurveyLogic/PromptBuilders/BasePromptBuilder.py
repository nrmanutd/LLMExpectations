from abc import ABC, abstractmethod
from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class BasePromptBuilder(ABC):
    @abstractmethod
    def buildPrompt(self, surveyDate: date, profile: ProfileData):
        pass