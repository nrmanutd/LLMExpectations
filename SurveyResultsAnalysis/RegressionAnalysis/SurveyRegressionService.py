import pandas as pd
import statsmodels.api as sm

class SurveyRegressionService:
    def __init__(self, inflationExpectations, pastYearInflation):
        self.pastYearInflation = pastYearInflation
        self.inflationExpectations = inflationExpectations

    def fit(self, survey):
        df = self._createDataset(survey)
        print(df)
        x = df[['X1', 'X2', 'X3']]
        y = df['Y']

        # Обучение модели
        x_const = sm.add_constant(x)
        model_sm = sm.OLS(y, x_const).fit()

        prediction = model_sm.predict(x_const)

        return y, prediction, model_sm

    def _createDataset(self, survey):
        rows = []

        df = self.inflationExpectations

        for i in range(1, len(df)):
            prev_date = df.index[i - 1]
            current_date = df.index[i]
            current_value = df['expected_inflation'].iloc[i]

            Y = current_value
            X1 = df['expected_inflation'].iloc[i - 1]
            X2 = self._getInflation(current_date)
            X3 = survey['exp_mean'].iloc[i]

            if X2 is None:
                continue

            if self._calcDifference(current_date, prev_date) > 1:
                continue

            row = {
                'Y': Y,
                'X1': X1,
                'X2': X2,
                'X3': X3
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

        return None

