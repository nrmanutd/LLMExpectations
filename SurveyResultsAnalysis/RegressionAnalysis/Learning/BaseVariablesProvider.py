from abc import ABC, abstractmethod


class BaseVariablesProvider(ABC):
    @abstractmethod
    def getBaseVariables(self, configuration: str) -> list[str]:
        pass