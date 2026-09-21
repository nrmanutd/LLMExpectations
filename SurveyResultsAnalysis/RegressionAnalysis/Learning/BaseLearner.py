from abc import ABC, abstractmethod


class BaseLearner(ABC):
    @abstractmethod
    def train(self, x_train, y_train):
        pass

    @abstractmethod
    def test(self, model, x_test):
        pass
