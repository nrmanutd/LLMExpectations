import pandas as pd
from datetime import date
from pathlib import Path

from pandas import DateOffset

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseCurrencyProvider import BaseCurrencyProvider


class USDRUBRateProvider(BaseCurrencyProvider):
    def __init__(self, path: Path):
        self.df, self.minDate, self.maxDate = self._load(path)
        self.deltaOneDay = pd.DateOffset(days=1)

    def getRateDifferenceByMonthOffset(self, d: date, offset: int):
        offset = pd.DateOffset(months=offset)
        return self._getRateDifference(d, offset)

    def getRateDifferenceByWeeksOffset(self, d: date, offset: int):
        offset = pd.DateOffset(weeks=offset)
        return self._getRateDifference(d, offset)

    def getRateDifferenceByDaysOffset(self, d: date, offset: int):
        offset = pd.DateOffset(days=offset)
        return self._getRateDifference(d, offset)

    def _load(self, path: Path):
        df = pd.read_excel(path, sheet_name=0, header=0)
        df['data'] = pd.to_datetime(df['data'], format='%d.%m.%Y')
        df['data'] = df['data'].dt.date

        df['curs'] = df['curs'].astype(float)

        df.set_index('data', inplace=True)
        df.sort_index(inplace=True)

        minDate = df.index.min()
        maxDate = df.index.max()

        return df, minDate, maxDate

    def _getRateDifference(self, d: date, offset: DateOffset):
        d = (d - self.deltaOneDay).date()
        newDate = (d - offset).date()

        currentRate = self._getRate(d)
        newRate = self._getRate(newDate)

        if newRate is None or currentRate is None:
            return None

        return (currentRate - newRate) / newRate

    def _getRate(self, d: date):
        if d < self.minDate:
            return None

        if d > self.maxDate:
            return None

        curd = d

        while True:
            if curd in self.df.index:
                return self.df.loc[curd, 'curs']

            curd = (curd - self.deltaOneDay).date()
