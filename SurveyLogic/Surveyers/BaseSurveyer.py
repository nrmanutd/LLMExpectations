from abc import ABC, abstractmethod


class BaseSurveyer(ABC):
    @abstractmethod
    def askSurvey(self, systemPrompt: str, prompt: str, respondentId: str):
        pass