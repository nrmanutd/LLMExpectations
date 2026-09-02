import pandas as pd
import statsmodels.api as sm
import numpy as np
from scipy.stats import stats


class SurveyRegressionService:
    def __init__(self, inflationExpectations, pastYearInflation, usdrubRate):
        self.usdrubRate = usdrubRate
        self.pastYearInflation = pastYearInflation
        self.inflationExpectations = inflationExpectations

    def fit(self, survey, vars, isDelta:bool):
        df = self._createDeltasDataset(survey) if isDelta else self._createDataset(survey)

        df.to_excel('temp.xlsx')

        x = df[vars]
        y = df['Y']
        yt = df['YT']

        dates = df['D']

        x_const = sm.add_constant(x)
        model_sm = sm.OLS(y, x_const).fit()

        prediction = model_sm.predict(x_const)
        adjustedPrediction = prediction + yt
        adjustedY = y + yt

        return adjustedY, adjustedPrediction, model_sm, dates

    def fit_oos(self, survey, vars, isDelta: bool, start_n=30):
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
            df = self._createDeltasDataset(survey)
        else:
            df = self._createDataset(survey)

        df.to_excel('temp.xlsx')

        x = df[vars].to_numpy(dtype=float)
        y = df['Y'].to_numpy(dtype=float)
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

            y_true_list.append(y_test + yt[i])
            pred_list.append(pred + yt[i])
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

    def estimateCorr(self, survey):
        df = self._createDataset(survey)

        r = df['X3']  # pandas Series
        y = df['Y']  # pandas Series

        y_diff = y.diff().dropna()
        r_minus_y_prev = (r - y.shift(1)).dropna()
        r_diff = r.diff().dropna()

        print('corr(y(t)-y(t-1), llm(t) - y(t-1))')
        self._estimateCorrInternal(y_diff, r_minus_y_prev)

        print('corr(y(t)-y(t-1), llm(t) - llm(t-1))')
        self._estimateCorrInternal(y_diff, r_diff)

    def _estimateCorrInternal(self, y_diff, r_diff):


        # Проверяем, что длины совпадают
        print(f"Длина x_diff: {len(y_diff)}")
        print(f"Длина r_minus_x_prev: {len(r_diff)}")

        # Считаем корреляцию
        correlation = np.corrcoef(y_diff, r_diff)[0, 1]
        print(f"Корреляция: {correlation}")
        return correlation

    def _createDataset(self, survey):
        rows = []
        print(survey)

        df = self.inflationExpectations

        for i in range(1, len(df)):
            prev_date = df.index[i - 1]
            current_date = df.index[i]
            llm_survey_date = survey.index[i]

            current_value = df['expected_inflation'].iloc[i]

            Y = current_value
            X1 = df['expected_inflation'].iloc[i - 1]
            X2 = self._getInflation(llm_survey_date)
            X3 = survey['exp_median'].iloc[i]
            X4 = self._get_usdrub(llm_survey_date)

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            if X2 is None or X4 is None:
                continue

            if self._calcDifference(current_date, prev_date) > 1:
                #print(f'Skipping date {current_date} because of prev date = {prev_date} is older for 1 month')
                continue

            row = {
                'Y': Y,
                'X1': X1,
                'X2': X2,
                'X3': X3,
                'X4': X4,
                'D': llm_survey_date,
                'YT': 0
            }
            rows.append(row)

        regression_df = pd.DataFrame(rows)
        return regression_df

    def _createDeltasDataset(self, survey):
        rows = []
        df = self.inflationExpectations

        for i in range(1, len(df)):
            prev_date = df.index[i - 1]
            current_date = df.index[i]
            llm_survey_date = survey.index[i]

            prev_value = df['expected_inflation'].iloc[i - 1]
            current_value = df['expected_inflation'].iloc[i]

            Y = current_value - prev_value
            X1 = self._get_usdrub(llm_survey_date)
            X2 = self._getInflationDelta(llm_survey_date)
            X3 = survey['exp_median'].iloc[i] - survey['exp_median'].iloc[i - 1]
            YT = prev_value

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            if X1 is None or X2 is None:
                continue

            if self._calcDifference(current_date, prev_date) > 1:
                #print(f'Skipping date {current_date} because of prev date = {prev_date} is older for 1 month')
                continue

            row = {
                'Y': Y,
                'X1': X1,
                'X2': X2,
                'X3': X3,
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

