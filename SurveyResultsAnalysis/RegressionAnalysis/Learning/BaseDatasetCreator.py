from abc import ABC, abstractmethod


class BaseDatasetCreator(ABC):
    @abstractmethod
    def getDataset(self, survey, variables: list[str], nMonth: int = 1):
        pass