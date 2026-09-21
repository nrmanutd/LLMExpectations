from abc import ABC, abstractmethod


class BaseDatasetCreator(ABC):
    @abstractmethod
    def getDataset(self, survey, nMonth: int = 1):
        pass