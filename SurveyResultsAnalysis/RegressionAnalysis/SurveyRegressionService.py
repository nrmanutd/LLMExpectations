import time

import numpy as np
import pandas as pd

from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseDatasetCreator import BaseDatasetCreator
from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseLearner import BaseLearner


class SurveyRegressionService:
    def __init__(self, datasetCreator: BaseDatasetCreator, learner: BaseLearner, filteringDates: set[np.datetime64] = None):
        self.learner = learner
        self.datasetCreator = datasetCreator

        self.filteringDates = set[np.datetime64]() if filteringDates is None else filteringDates

    def fitWithConfig(self, survey, v, isOOS:bool, isExpandingOOS:bool, nMonth: int=1, start_n: int=30, train_share:float=0.8):
        if isOOS:
            if isExpandingOOS:
                y, r, m, dates = self.fit_oos(survey, v, nMonth=nMonth,
                                                                 start_n=start_n)
            else:
                y, r, m, dates = self.fit_oos_fixedsplit(survey, v, nMonth=nMonth, train_share=train_share)
        else:
            y, r, m, dates = self.fit(survey, v, nMonth=nMonth)

        return y, r, m, dates

    def fit(self, survey, vars, nMonth=1):
        df = self.datasetCreator.getDataset(survey, vars[0], nMonth)

        x = df[vars[0]]
        y = df[vars[1]]
        yt = df['YT']

        dates = df['D'].to_numpy()
        dates_list = []
        for i in range(len(dates)):
            dates_list.append(dates[i])

        model = self.learner.train(x, y)
        prediction = self.learner.test(model, x)

        adjustedPrediction = prediction + yt
        adjustedY = y + yt

        ay = pd.Series(
            adjustedY.to_numpy().tolist(),
            index=dates_list,
            name='actual'
        )

        ap = pd.Series(
            adjustedPrediction.to_numpy().tolist(),
            index=dates_list,
            name='prediction'
        )

        return ay, ap, model, dates_list

    def fit_oos(self, survey, vars, start_n=30, nMonth=1):
        """
        Построение регрессии с расширяющимся окном (expanding window)
        для прогнозирования следующей точки.

        Parameters:
        -----------
        survey : данные опроса
        vars : список переменных для модели
        start_n : int
            Начальный размер обучающей выборки.

        Returns:
        --------
        y_true : pd.Series
            Фактические значения для OOS-периода.
        predictions : pd.Series
            OOS-прогнозы.
        model_sm : str
            Пустая строка для совместимости.
        dates : list
            Даты прогнозируемых точек.
        """

        df = self.datasetCreator.getDataset(survey, vars[0], nMonth)
        df.to_excel('tempoos.xlsx')

        x = df[vars[0]].to_numpy(dtype=float)
        y = df[vars[1]].to_numpy(dtype=float)
        yt = df['YT'].to_numpy(dtype=float)
        dates = df['D'].to_numpy()

        total_n = len(df)

        if total_n <= start_n:
            raise ValueError(
                f"Недостаточно данных: total_n={total_n}, start_n={start_n}"
            )

        y_true_list = []
        pred_list = []
        dates_list = []

        loggingStep = (total_n - start_n) / 20
        nextValue = loggingStep
        st = time.time()

        for i in range(start_n, total_n):
            if i - start_n >= nextValue:
                print(f'[{time.time() - st:.1f}s] OOS progress: {(i - start_n) / (total_n - start_n) * 100:.1f}%')
                nextValue += loggingStep
            # Expanding window:
            # обучаемся на [0, ..., i-1]
            x_train = x[:i]
            y_train = y[:i]

            # ВАЖНО:
            # i:i+1 сохраняет двумерную форму (1, n_features)
            x_test = x[i:i + 1]
            y_test = y[i]

            model = self.learner.train(x_train, y_train)
            pred = self.learner.test(model, x_test).item()

            if dates[i] not in self.filteringDates:
                y_true_list.append(y_test + yt[i])
                pred_list.append(pred + yt[i])
            else:
                #print(f'Fixing: {y_test + yt[i]} instead of prediction {pred + yt[i]} at date {dates[i]}')
                y_true_list.append(y_test + yt[i])
                pred_list.append(y_test + yt[i])

            dates_list.append(dates[i])

        y_true_result = pd.Series(
            y_true_list,
            index=dates_list,
            name='actual'
        )

        pred_result = pd.Series(
            pred_list,
            index=dates_list,
            name='prediction'
        )

        return y_true_result, pred_result, "", dates_list

    def fit_oos_fixedsplit(
            self,
            survey,
            vars,
            train_share: float = 0.8,
            nMonth: int = 1
    ):
        """
        OOS-прогноз с фиксированным хронологическим train/test split.

        Первые train_share наблюдений используются для обучения модели.
        Оставшиеся (1 - train_share) наблюдений используются как OOS test.

        В отличие от expanding-window подхода, модель обучается ровно один раз
        и затем прогнозирует весь тестовый период.

        Parameters
        ----------
        survey
            Данные опроса.

        vars
            Список переменных для модели.

        isDelta : bool
            Если True, используется датасет приростов.
            Если False, используется датасет уровней.

        train_share : float, default=0.8
            Доля первых наблюдений, используемых для обучения.
            Например, 0.8 = первые 80% train, последние 20% test.

        nMonth : int, default=1
            Горизонт прогноза.

        Returns
        -------
        y_true : pd.Series
            Фактические значения для OOS test-периода.

        predictions : pd.Series
            OOS-прогнозы для test-периода.

        model_sm : str
            Пустая строка для совместимости.

        dates : list
            Даты прогнозируемых точек.
        """

        if not 0 < train_share < 1:
            raise ValueError(
                f"train_share должен быть между 0 и 1, получено: {train_share}"
            )

        df = self.datasetCreator.getDataset(survey, vars[0], nMonth)


        x = df[vars[0]].to_numpy(dtype=float)
        y = df[vars[1]].to_numpy(dtype=float)
        yt = df['YT'].to_numpy(dtype=float)
        dates = df['D'].to_numpy()

        total_n = len(df)

        # Первые train_share наблюдений идут в train.
        # int() дает floor, т.е. при n=141 и train_share=0.8:
        # train_n = 112, test_n = 29.
        train_n = int(total_n * train_share)

        if train_n < 1:
            raise ValueError(
                f"Слишком маленькая обучающая выборка: "
                f"total_n={total_n}, train_share={train_share}"
            )

        if train_n >= total_n:
            raise ValueError(
                f"Нет наблюдений для test: "
                f"total_n={total_n}, train_n={train_n}"
            )

        # ---------------------------------------------------------
        # Fixed chronological split
        # ---------------------------------------------------------
        #print(f'Date = {dates[train_n]}')

        x_train = x[:train_n]
        y_train = y[:train_n]

        x_test = x[train_n:]
        y_test = y[train_n:]

        yt_test = yt[train_n:]
        dates_test = dates[train_n:]

        model = self.learner.train(x_train, y_train)
        predictions = self.learner.test(model, x_test)

        # ---------------------------------------------------------
        # Формируем результат точно в той же логике,
        # что и в исходной функции
        # ---------------------------------------------------------

        y_true_list = []
        pred_list = []
        dates_list = []

        for i in range(len(y_test)):

            actual_value = y_test[i] + yt_test[i]
            predicted_value = predictions[i] + yt_test[i]
            date = dates_test[i]

            if date not in self.filteringDates:
                y_true_list.append(actual_value)
                pred_list.append(predicted_value)
            else:
                print(
                    f'Fixing: {actual_value} '
                    f'instead of prediction {predicted_value} '
                    f'at date {date}'
                )

                y_true_list.append(actual_value)
                pred_list.append(actual_value)

            dates_list.append(date)

        y_true_result = pd.Series(
            y_true_list,
            index=dates_list,
            name='actual'
        )

        pred_result = pd.Series(
            pred_list,
            index=dates_list,
            name='prediction'
        )

        return y_true_result, pred_result, "", dates_list

    def estimateCorr(self, survey, vars, nMonth=1):
        df = self.datasetCreator.getDataset(survey, vars[0], nMonth)

        r = df['X3']  # pandas Series
        y = df['Y']  # pandas Series

        y_diff = y.diff().dropna()
        r_minus_y_prev = (r - y.shift(1)).dropna()
        r_diff = r.diff().dropna()

        #print('corr(y(t)-y(t-1), llm(t) - y(t-1))')
        #self._estimateCorrInternal(y_diff, r_minus_y_prev)

        #print('corr(y(t)-y(t-1), llm(t) - llm(t-1))')
        self._estimateCorrInternal(y_diff, r_diff)

    def _estimateCorrInternal(self, y_diff, r_diff):
        # Проверяем, что длины совпадают
        print(f"Длина y(t) - y(t-1): {len(y_diff)}")
        print(f"Длина llm(t) - llm(t-1): {len(r_diff)}")

        # Считаем корреляцию
        correlation = np.corrcoef(y_diff, r_diff)[0, 1]
        print(f"Корреляция: {correlation}")
        return correlation




