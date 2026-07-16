from abc import ABC, abstractmethod
from datetime import date


class BaseProfilesProvider(ABC):
    @abstractmethod
    def getProfiles(self, surveyDate: date):
        pass