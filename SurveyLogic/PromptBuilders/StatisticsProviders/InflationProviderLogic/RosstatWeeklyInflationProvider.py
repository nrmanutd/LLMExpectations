import pandas as pd
from datetime import date
from pathlib import Path

from pandas import DataFrame

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseWeeklyInflationProvider import \
    BaseWeeklyInflationProvider
from SurveyLogic.PromptBuilders.commonHelpers import parseRosstateMonth


class RosstatWeeklyInflationProvider(BaseWeeklyInflationProvider):
    def __init__(self, path: Path, year):
        datesMap, productsMap, df = self._getMaps(path, year)

        self.productsMap = productsMap
        self.datesMap = datesMap
        self.df = df

    def getWeeklyInflation(self, d: date, products: list[str], weeksOffset: int) -> list[float]:
        result = []

        for p in products:
            curInflation = self._getProductWeeklyInflation(d, p, weeksOffset)
            result.append(curInflation)

        return result

    def _getProductWeeklyInflation(self, d: date, product: str, weeksOffset: int):
        rowIdx = self.productsMap[product]

        inflation = 1
        for i in range(weeksOffset):
            currentDate = (d - pd.DateOffset(days=7*i + 1)).date()
            columnIdx = self.datesMap[currentDate]

            curInflation = float(self.df.iloc[rowIdx, columnIdx])
            inflation = inflation * curInflation/100

        return inflation**(365 / (7 * weeksOffset)) - 1

    def _getMaps(self, path: Path, year: int) -> (dict[str, int], dict[date, int], DataFrame):
        df = pd.read_excel(path, sheet_name=str(year), header=None, skiprows=[0, 1, 2])

        data_start_col = 1
        month_row = 0

        data_start_row = 1
        goodCategory_col = 0

        dateToCol = dict()
        for col in range(data_start_col, len(df.columns)):
            val = df.iloc[month_row, col]
            dateVal = parseRosstateMonth(val, year)
            dateToCol[dateVal] = col

        goodToRow = {}
        for row in range(data_start_row, len(df)):
            category = df.iloc[row, goodCategory_col]
            category = str(category).strip()

            goodToRow[category] = row

        return dateToCol, goodToRow, df

