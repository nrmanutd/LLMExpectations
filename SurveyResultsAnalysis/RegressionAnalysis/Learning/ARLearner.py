from sklearn.linear_model import LinearRegression
import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class ARLearner(BaseLearner):
    """
    Авторегрессия порядка p.
    Предполагается, что x_train уже содержит p лаговых признаков
    (x_{t-1}, x_{t-2}, ..., x_{t-p}) в нужном порядке.
    """
    def __init__(self, isDummy: bool, p: int):
        self.isDummy = isDummy
        self.p = p

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        if self.isDummy:
            x_test[:, -1] = 0

        y_pred = model.predict(x_test)
        return y_pred

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)

        # Обычная линейная регрессия на лагах = AR(p)
        model = LinearRegression(fit_intercept=True)
        model.fit(x_train, y_train)
        return model