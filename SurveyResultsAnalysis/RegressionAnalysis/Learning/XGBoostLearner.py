from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class XGBoostLearner(BaseLearner):
    def __init__(self, isDummy: bool):
        self.isDummy = isDummy

    def test(self, model, x_test):
        pass

    def train(self, x_train, y_train):
        pass