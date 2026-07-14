from abc import ABC, abstractmethod


class BaseSurveyer(ABC):
    @abstractmethod
    def askSurvey(self, prompt: str):
        pass