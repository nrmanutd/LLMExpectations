import pandas as pd
import numpy as np

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseKeyRateProvider import BaseKeyRateProvider
from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseDatasetCreator import BaseDatasetCreator


class StandardDatasetCreator(BaseDatasetCreator):
    def __init__(self, inflationExpectations, pastYearInflation, usdrubRate, keyRateProvider: BaseKeyRateProvider, targetVariable: str, isDelta: bool, isDummy: bool, datesToExclude = None, datesToInclude = None):
        self.pastYearInflation = pastYearInflation
        self.datesToInclude = (np.datetime64('1900-01-01'),
                               np.datetime64('2100-01-01')) if datesToInclude is None else datesToInclude
        self.datesToExclude = (np.datetime64('2100-01-01'),
                               np.datetime64('2100-01-01')) if datesToExclude is None else datesToExclude
        self.isDummy = isDummy
        self.targetVariable = targetVariable
        self.inflationExpectations = inflationExpectations
        self.isDelta = isDelta
        self.usdrubRate = usdrubRate
        self.keyRateProvider = keyRateProvider

    def getDataset(self, survey, variables: list[str], nMonth: int = 1):
        if self.isDelta:
            return self._createDeltasDataset(survey, variables, nMonth)
        else:
            return self._createDataset(survey, variables, nMonth)

    def _createDataset(self, survey, variables, nMonth):
        rows = []

        df = self.inflationExpectations

        for i in range(nMonth, len(df)):
            prev_date = df.index[i - nMonth]
            current_date = df.index[i]
            llm_survey_date = survey.index[i - nMonth + 1]

            #CPI as target variable
            if self.targetVariable == 'CPI':
                if i + 1 < len(df):
                    next_current_date = df.index[i + 1]
                    current_value = self._getInflation(next_current_date)
                    prev_currentValue = self._getInflation(llm_survey_date)
                    dummyValue = self._getDummy(next_current_date)
                else:
                    continue
            elif self.targetVariable == 'IE':
                #IE as target variable
                current_value = df['expected_inflation'].iloc[i]
                prev_currentValue = df['expected_inflation'].iloc[i - nMonth]
                dummyValue = self._getDummy(current_date)
            else:
                raise ValueError(f'Unknown target variable name: {self.targetVariable}')

            #deltaKR = self.keyRateProvider.getKeyRateIncrements(llm_survey_date, 1)
            #if len(deltaKR) == 0:
            #    continue

            Y = current_value
            X1 = prev_currentValue
            #X2 = self._getInflation(llm_survey_date)
            X3 = survey['exp_median'].iloc[i - nMonth + 1]
            #X4 = self._get_usdrub(llm_survey_date)
            #X6 = deltaKR[0]
            X7 = dummyValue

            if Y is None or X1 is None or X3 is None or X7 is None:
                continue

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            #if X2 is None or X4 is None:
            #    continue

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
                #'X2': X2,
                'X3': X3,
                #'X4': X4,
                #'X6': X6,
                'X7': X7,
                'D': llm_survey_date,
                'YT': 0
            }
            rows.append(row)

        regression_df = pd.DataFrame(rows)
        return regression_df

    def _createDeltasDataset(self, survey, variables, nMonth):
        rows = []
        df = self.inflationExpectations

        for i in range(2*nMonth, len(df)):
            prev_date = df.index[i - nMonth]
            current_date = df.index[i]
            llm_survey_date = survey.index[i - nMonth + 1]

            prev_prev_value = df['expected_inflation'].iloc[i - 2*nMonth]
            prev_value = df['expected_inflation'].iloc[i - nMonth]
            current_value = df['expected_inflation'].iloc[i]

            #deltaKR = self.keyRateProvider.getKeyRateIncrements(llm_survey_date, 1)
            #if len(deltaKR) == 0:
            #    continue

            Y = current_value - prev_value
            X1 = prev_value
            #X2 = self._getInflationDelta(llm_survey_date)
            X3 = survey['exp_median'].iloc[i - nMonth + 1] - survey['exp_median'].iloc[i - 2*nMonth + 1]
            #X4 = self._get_usdrub(llm_survey_date)
            X5 = prev_value - prev_prev_value
            #X6 = deltaKR[0]
            X7 = self._getDummy(current_date)
            YT = prev_value

            #print(f'Y = {Y}, X1 = {X1}, X2 = {X2}, X3 = {X3}, D = {current_date}')
            #if X4 is None or X2 is None:
            #    continue

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
                #'X2': X2,
                'X3': X3,
                #'X4': X4,
                'X5': X5,
                #'X6': X6,
                'X7': X7,
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

    def _getDummy(self, ieSurveyDate):
        if not self.isDummy:
            return 0

        dummyDate = pd.Timestamp('2022-03-11 00:00:00')

        if ieSurveyDate == dummyDate:
            return 1

        return 0