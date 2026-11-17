import numpy as np
import statsmodels.api as sm
from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class RegressionLearner(BaseLearner):
    def __init__(self, isDummy: bool):
        self.isDummy = isDummy

    def test(self, model, x_test):
        #from fit
        #x_const = sm.add_constant(x)
        #model_sm = sm.OLS(y, x_const).fit(cov_type='HAC', cov_kwds={'maxlags': 4}, use_t=True)
        #prediction = model_sm.predict(x_const)

        x_test_const = np.column_stack([
            np.ones(x_test.shape[0]),
            x_test
        ])

        if self.isDummy:
            x_test_const[:, -1] = 0

        pred = model.predict(x_test_const)
        return pred

    def train(self, x_train, y_train):
        x_train_const = np.column_stack([
            np.ones(x_train.shape[0]),
            x_train
        ])
        #x_const = sm.add_constant(x)?

        # OLS
        model = sm.OLS(
            y_train,
            x_train_const
        ).fit(cov_type='HAC',cov_kwds={'maxlags': 4},use_t=True)
        #fit?

        return model

