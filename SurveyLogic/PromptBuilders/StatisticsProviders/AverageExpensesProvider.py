from datetime import datetime, date

import pandas as pd

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseAverageExpensesProvider import BaseAverageExpensesProvider


class AverageExpensesProvider(BaseAverageExpensesProvider):
    def __init__(self, path: str):
        self.df = pd.read_excel(path, sheet_name=0, header=None, skiprows=[0, 1])

        data_start_col = 4
        year_row = 0
        data_start_row = 0
        region_col = 1

        # Строим словарь: год -> номер колонки
        self.year_to_col = {}
        for col in range(data_start_col, len(self.df.columns)):
            val = self.df.iloc[year_row, col]
            if pd.notna(val):
                try:
                    year = int(float(val))
                    self.year_to_col[year] = col
                except (ValueError, TypeError):
                    pass

        # Строим словарь: регион -> номер строки
        self.region_to_row = {}
        for row in range(data_start_row, len(self.df)):
            val = self.df.iloc[row, region_col]
            if pd.notna(val):
                region = str(val).strip()
                self.region_to_row[region] = row

        # Сохраняем параметры
        self.data_start_col = data_start_col

    def getRegionAverageExpenses(self, region: str, d: date) -> float:
        region_row = None

        for reg, row in self.region_to_row.items():
            if region.lower() in reg.lower():
                region_row = row
                break

        if region_row is None:
            raise KeyError(f"Регион '{region}' не найден")

        year = d.year - 1
        # Ищем год
        if year not in self.year_to_col:
            raise KeyError(f"Год {year} не найден")

        col = self.year_to_col[year]
        value = self.df.iloc[region_row, col]

        if not pd.isna(value):
            return float(value)

        value = self.df.iloc[region_row - 1, col]
        if not pd.isna(value):
            return float(value)

        raise ValueError(f'Cant extract value for region {region} and date {date.strftime('%d.%m.%Y')}')
