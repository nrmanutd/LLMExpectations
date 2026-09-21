import numpy as np
from xgboost import XGBRegressor

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class XGBoostLearner(BaseLearner):
    def __init__(self, isDummy: bool):
        self.isDummy = isDummy

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        y_pred = model.predict(x_test)
        return y_pred

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)

        model = XGBRegressor(
            n_estimators=500,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            tree_method="hist",
            n_jobs=-1,
            random_state=42,
        )

        # 3. Обучаем с early stopping на валидации
        model.fit(
            x_train, y_train,
            eval_set=[(x_train, y_train)],  # лучше — отдельный валидационный набор
            verbose=False,
        )

        return model