import numpy as np
from abc import ABC, abstractmethod


class BaseSurveyRegressionService(ABC):

    @abstractmethod
    def fitWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1,
                      cutoff_date: np.datetime64 | None = None, train_share: float = 0.8):
        pass

    @abstractmethod
    def fitBaseVariablesWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1,
                      cutoff_date: np.datetime64 | None = None, train_share: float = 0.8):
        pass
