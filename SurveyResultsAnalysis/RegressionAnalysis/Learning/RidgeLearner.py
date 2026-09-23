from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class RidgeLearner(BaseLearner):
    def __init__(
        self,
        isDummy: bool,
        alpha: float = 1.0,
        strategy: str = "median",   # "mean", "median", "most_frequent", "constant"
        fill_value: float = 0.0,    # используется только при strategy="constant"
        scale: bool = True,         # Ridge чувствителен к масштабу → лучше True
    ):
        self.isDummy = isDummy
        self.alpha = alpha
        self.strategy = strategy
        self.fill_value = fill_value
        self.scale = scale

    def _build_model(self):
        steps = [
            ("imputer", SimpleImputer(
                strategy=self.strategy,
                fill_value=self.fill_value if self.strategy == "constant" else None,
                keep_empty_features=True,   # сохранить полностью-NaN колонки как 0
            )),
        ]
        if self.scale:
            steps.append(("scaler", StandardScaler()))
        steps.append(("ridge", Ridge(alpha=self.alpha, random_state=42)))
        return Pipeline(steps)

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)
        model = self._build_model()
        model.fit(x_train, y_train)
        return model

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        if self.isDummy:
            x_test[:, -1] = 0

        # NaN остаются в x_test — Pipeline сам их импутирует
        y_pred = model.predict(x_test)
        return y_pred