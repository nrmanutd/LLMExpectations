from sklearn.linear_model import ElasticNet
import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class ElasticNetLearner(BaseLearner):
    def __init__(
        self,
        isDummy: bool,
        alpha: float = 1.0,
        l1_ratio: float = 0.5,
        fit_intercept: bool = True,
        max_iter: int = 10000,
        tol: float = 1e-4,
    ):
        self.isDummy = isDummy
        self.alpha = alpha
        self.l1_ratio = l1_ratio
        self.fit_intercept = fit_intercept
        self.max_iter = max_iter
        self.tol = tol

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        if self.isDummy:
            x_test[:, -1] = 0

        y_pred = model.predict(x_test)
        return y_pred

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)

        model = ElasticNet(
            alpha=self.alpha,
            l1_ratio=self.l1_ratio,
            fit_intercept=self.fit_intercept,
            max_iter=self.max_iter,
            tol=self.tol,
            random_state=42,
        )
        model.fit(x_train, y_train)
        return model