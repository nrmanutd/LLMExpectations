import pandas as pd
import statsmodels.api as sm
import numpy as np
from scipy.stats import stats

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseKeyRateProvider import BaseKeyRateProvider


class SurveyRegressionService:
    def __init__(self, inflationExpectations, pastYearInflation, usdrubRate, keyRateProvider: BaseKeyRateProvider, datesToExclude, datesToInclude = None, filteringDates: set[np.datetime64] = None):
        self.datesToInclude = (np.datetime64('1900-01-01'), np.datetime64('2100-01-01')) if datesToInclude is None else datesToInclude
        self.datesToExclude = (np.datetime64('2100-01-01'), np.datetime64('2100-01-01')) if datesToExclude is None else datesToExclude
        self.keyRateProvider = keyRateProvider
        self.filteringDates = set[np.datetime64]() if filteringDates is None else filteringDates
        self.usdrubRate = usdrubRate
        self.pastYearInflation = pastYearInflation
        self.inflationExpectations = inflationExpectations

    def fitWithConfig(self, survey, v, isDelta: bool, isOOS:bool, isExpandingOOS:bool, nMonth: int=1, start_n: int=30, train_share:float=0.8):
        if isOOS:
            if isExpandingOOS:
                y, r, m, dates = self.fit_oos(survey, v, isDelta=isDelta, nMonth=nMonth,
                                                                 start_n=start_n)
            else:
                y, r, m, dates = self.fit_oos_fixedsplit(survey, v, isDelta=isDelta, nMonth=nMonth)
        else:
            y, r, m, dates = self.fit(survey, v, isDelta=isDelta, nMonth=nMonth)

        return y, r, m, dates

    def fit(self, survey, vars, isDelta:bool, nMonth=1):
        df = self._createDeltasDataset(survey, nMonth) if isDelta else self._createDataset(survey, nMonth)

        x = df[vars[0]]
        y = df[vars[1]]
        yt = df['YT']

        dates = df['D'].to_numpy()
        dates_list = []
        for i in range(len(dates)):
            dates_list.append(dates[i])

        x_const = sm.add_constant(x)
        model_sm = sm.OLS(y, x_const).fit(cov_type='HAC',cov_kwds={'maxlags': 4},use_t=True)

        prediction = model_sm.predict(x_const)
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

        return ay, ap, model_sm, dates_list

    def fit_oos(self, survey, vars, isDelta: bool, start_n=30, nMonth=1):
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

        if isDelta:
            df = self._createDeltasDataset(survey, nMonth)
        else:
            df = self._createDataset(survey, nMonth)

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

        for i in range(start_n, total_n):
            # Expanding window:
            # обучаемся на [0, ..., i-1]
            x_train = x[:i]
            y_train = y[:i]

            # ВАЖНО:
            # i:i+1 сохраняет двумерную форму (1, n_features)
            x_test = x[i:i + 1]
            y_test = y[i]

            # Добавляем intercept
            x_train_const = np.column_stack([
                np.ones(x_train.shape[0]),
                x_train
            ])

            x_test_const = np.column_stack([
                np.ones(x_test.shape[0]),
                x_test
            ])

            # OLS
            model = sm.OLS(
                y_train,
                x_train_const
            ).fit()

            # Прогноз ровно одной следующей точки
            pred = model.predict(x_test_const).item()

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
            isDelta: bool,
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

        if isDelta:
            df = self._createDeltasDataset(survey, nMonth)
        else:
            df = self._createDataset(survey, nMonth)

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

        # ---------------------------------------------------------
        # Intercept
        # ---------------------------------------------------------

        x_train_const = np.column_stack([
            np.ones(x_train.shape[0]),
            x_train
        ])

        x_test_const = np.column_stack([
            np.ones(x_test.shape[0]),
            x_test
        ])

        # ---------------------------------------------------------
        # Обучаем модель РОВНО ОДИН РАЗ
        # ---------------------------------------------------------

        model = sm.OLS(
            y_train,
            x_train_const
        ).fit()

        # Прогноз сразу для всех оставшихся 20%
        predictions = model.predict(x_test_const)

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

    def estimateCorr(self, survey, nMonth=1):
        df = self._createDataset(survey, nMonth)

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

    def _createDataset(self, survey, nMonth):
        rows = []

        df = self.inflationExpectations

        for i in range(nMonth, len(df)):
            prev_date = df.index[i - nMonth]
            current_date = df.index[i]
            llm_survey_date = survey.index[i - nMonth + 1]

            #CPI as target variable
            #if i + 1 < len(df):
            #    llm_surveyNexDate = survey.index[i - nMonth + 2]
            #    inflation =self._getInflation(llm_surveyNexDate)
            #    current_value = inflation
            #else:
            #    continue

            current_value = df['expected_inflation'].iloc[i]

            deltaKR = self.keyRateProvider.getKeyRateIncrements(llm_survey_date, 1)
            if len(deltaKR) == 0:
                continue

            Y = current_value
            X1 = df['expected_inflation'].iloc[i - nMonth]
            X2 = self._getInflation(llm_survey_date)
            X3 = survey['exp_median'].iloc[i - nMonth + 1]
            X4 = self._get_usdrub(llm_survey_date)
            X6 = deltaKR[0]

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            if X2 is None or X4 is None:
                continue

            if self.datesToExclude[0] <= llm_survey_date < self.datesToExclude[1]:
                #print(f'Excluding...{current_date}')
                continue

            if llm_survey_date < self.datesToInclude[0] or llm_survey_date > self.datesToInclude[1]:
                #print(f'Excluding...{current_date}')
                continue

            if self._calcDifference(current_date, prev_date) > nMonth:
                #print(f'Skipping date {current_date} because of prev date = {prev_date} is older for {nMonth} month')
                continue

            row = {
                'Y': Y,
                'X1': X1,
                'X2': X2,
                'X3': X3,
                'X4': X4,
                'X6': X6,
                'D': llm_survey_date,
                'YT': 0
            }
            rows.append(row)

        regression_df = pd.DataFrame(rows)
        return regression_df

    def _createDeltasDataset(self, survey, nMonth):
        rows = []
        df = self.inflationExpectations

        for i in range(2*nMonth, len(df)):
            prev_date = df.index[i - nMonth]
            current_date = df.index[i]
            llm_survey_date = survey.index[i - nMonth + 1]

            prev_prev_value = df['expected_inflation'].iloc[i - 2*nMonth]
            prev_value = df['expected_inflation'].iloc[i - nMonth]
            current_value = df['expected_inflation'].iloc[i]

            deltaKR = self.keyRateProvider.getKeyRateIncrements(llm_survey_date, 1)
            if len(deltaKR) == 0:
                continue

            Y = current_value - prev_value
            X1 = prev_value
            X2 = self._getInflationDelta(llm_survey_date)
            X3 = survey['exp_median'].iloc[i - nMonth + 1] - survey['exp_median'].iloc[i - 2*nMonth + 1]
            X4 = self._get_usdrub(llm_survey_date)
            X5 = prev_value - prev_prev_value
            X6 = deltaKR[0]
            YT = prev_value

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            if X4 is None or X2 is None:
                continue

            if self.datesToExclude[0] <= llm_survey_date < self.datesToExclude[1]:
                #print(f'Excluding...{current_date}')
                continue

            if llm_survey_date < self.datesToInclude[0] or llm_survey_date > self.datesToInclude[1]:
                #print(f'Excluding...{current_date}')
                continue

            if self._calcDifference(current_date, prev_date) > nMonth:
                #print(f'Skipping date {current_date} because of prev date = {prev_date} is older for {nMonth} month')
                continue

            row = {
                'Y': Y,
                'X1': X1,
                'X2': X2,
                'X3': X3,
                'X4': X4,
                'X5': X5,
                'X6': X6,
                'D': llm_survey_date,
                'YT': YT
            }
            rows.append(row)

        regression_df = pd.DataFrame(rows)
        return regression_df

    def _calcDifference(self, date1, date2):
        monthDiff = (date1.year - date2.year) * 12 + date1.month - date2.month
        return monthDiff

    def _getInflation(self, date):
        df = self.pastYearInflation
        actualValue = None
        actualValueDate = None

        for i in range(len(df)):
            current_date = df.index[i]
            current_value = df['Значение'].iloc[i]

            if current_date > date:
                if actualValueDate is None:
                    return None

                month_diff = self._calcDifference(date, actualValueDate)
                if month_diff > 1:
                    return None
                return actualValue

            actualValue = current_value
            actualValueDate = current_date

        if actualValueDate is None:
            return None

        month_diff = self._calcDifference(date, actualValueDate)
        if month_diff > 1:
            return None
        return actualValue

    def _getInflationDelta(self, date):
        df = self.pastYearInflation
        actualValue = None
        actualValueDate = None

        for i in range(1, len(df)):
            current_date = df.index[i]
            prev_value = df['Значение'].iloc[i - 1]
            current_value = df['Значение'].iloc[i]

            if current_date > date:
                if actualValueDate is None:
                    return None

                month_diff = self._calcDifference(date, actualValueDate)
                if month_diff > 1:
                    return None
                return actualValue

            actualValue = current_value - prev_value
            actualValueDate = current_date

        if actualValueDate is None:
            return None

        month_diff = self._calcDifference(date, actualValueDate)
        if month_diff > 1:
            return None
        return actualValue

    def _get_usdrub(self, target_date, positions_back=10):
        """
        Всегда берет дату из прошлого (или саму дату, если есть).
        """
        # Фильтруем только даты <= target_date
        df = self.usdrubRate
        past_dates = df.index[df.index <= target_date]

        if len(past_dates) == 0:
            return None  # нет данных в прошлом

        # Берем самую позднюю дату из прошлого
        found_date = past_dates[-1]
        current_idx = df.index.get_loc(found_date)

        past_idx = current_idx - positions_back

        if past_idx < 0:
            return None

        current_value = df.iloc[current_idx, 1]
        past_value = df.iloc[past_idx, 1]

        return current_value/past_value - 1

    def _get_values_by_position(self, df, current_date, positions_back=10):
        """
        Получает значения по позиции (не по дате).
        """
        # Находим позицию текущей даты
        try:
            current_idx = df.index.get_loc(current_date)
        except KeyError:
            # Если даты нет, ищем ближайшую
            current_idx = df.index.get_indexer([current_date], method='nearest')[0]
            current_date = df.index[current_idx]

        # Получаем значение 10 позиций назад
        past_idx = current_idx - positions_back

        if past_idx < 0:
            raise ValueError(f"Недостаточно данных: нужно {positions_back} позиций назад")

        current_value = df.iloc[current_idx]
        past_value = df.iloc[past_idx]
        past_date = df.index[past_idx]

        return {
            'current_date': current_date,
            'current_value': current_value,
            'past_date': past_date,
            'past_value': past_value,
            'positions_back': positions_back
        }

