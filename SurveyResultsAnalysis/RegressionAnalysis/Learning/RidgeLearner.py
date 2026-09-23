from sklearn.linear_model import Ridge
import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class RidgeLearner(BaseLearner):
    def __init__(
        self,
        isDummy: bool,
        alpha: float = 1.0,
        fit_intercept: bool = True,
        solver: str = "auto",
    ):
        self.isDummy = isDummy
        self.alpha = alpha
        self.fit_intercept = fit_intercept
        self.solver = solver

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        if self.isDummy:
            x_test[:, -1] = 0

        y_pred = model.predict(x_test)
        return y_pred

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)

        model = Ridge(
            alpha=self.alpha,
            fit_intercept=self.fit_intercept,
            solver=self.solver,
            random_state=42,
        )
        model.fit(x_train, y_train)
        return model