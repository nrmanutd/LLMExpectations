from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner
import numpy as np
from sklearn.linear_model import LinearRegression

class ARXLearner(BaseLearner):
    """
        Авторегрессия порядка p, устойчивая к NaN в признаках.
        Предполагается, что x_train уже содержит p лаговых признаков
        (x_{t-1}, x_{t-2}, ..., x_{t-p}) в нужном порядке.

        Стратегия обработки NaN:
          - на train вычисляются статистики заполнения (медиана по столбцу);
          - если столбец целиком из NaN — заполняем нулём (признак неинформативен);
          - на train и test NaN заменяются соответствующими значениями;
          - строки с NaN в y_train отбрасываются при обучении.
        """

    def __init__(self, isDummy: bool, p: int):
        self.isDummy = isDummy
        self.p = p
        self._fill_values = None  # np.ndarray формы (n_features,)

    # ---------- внутренние утилиты ----------

    @staticmethod
    def _compute_fill_values(x: np.ndarray) -> np.ndarray:
        """
        Вычисляет значения для заполнения NaN по каждому столбцу.
        Медиана устойчивее среднего к выбросам. Если столбец весь из NaN —
        ставим 0.0.
        """
        n_features = x.shape[1]
        fill = np.zeros(n_features, dtype=np.float32)
        for j in range(n_features):
            col = x[:, j]
            mask = ~np.isnan(col)
            if mask.any():
                fill[j] = np.median(col[mask]).astype(np.float32)
            else:
                fill[j] = 0.0
        return fill

    @staticmethod
    def _apply_fill(x: np.ndarray, fill: np.ndarray) -> np.ndarray:
        """
        Заменяет NaN в x на значения из fill (по столбцам).
        Работает по месту в копии массива.
        """
        x = x.copy()
        nan_mask = np.isnan(x)
        if nan_mask.any():
            # broadcasting: fill формы (n_features,) накладывается на столбцы
            x[nan_mask] = np.take(fill, np.where(nan_mask)[1])
        return x

    # ---------- публичный API ----------

    def test(self, model, x_test):
        x_test = x_test.astype(np.float32)

        if self.isDummy:
            x_test[:, -1] = 0

        if self._fill_values is not None:
            x_test = self._apply_fill(x_test, self._fill_values)

        y_pred = model.predict(x_test)
        return y_pred

    def train(self, x_train, y_train):
        x_train = x_train.astype(np.float32)
        y_train = np.asarray(y_train)

        # Вычисляем статистики заполнения ДО любых манипуляций
        self._fill_values = self._compute_fill_values(x_train)

        # Заполняем NaN в признаках
        x_train = self._apply_fill(x_train, self._fill_values)

        # Отбрасываем строки, где целевая переменная — NaN
        y_nan_mask = np.isnan(y_train)
        if y_nan_mask.any():
            keep = ~y_nan_mask
            x_train = x_train[keep]
            y_train = y_train[keep]

        if x_train.shape[0] == 0:
            raise ValueError(
                "ARLearner.train: после удаления NaN в y_train не осталось "
                "ни одной обучающей строки."
            )

        model = LinearRegression(fit_intercept=True)
        model.fit(x_train, y_train)
        return model