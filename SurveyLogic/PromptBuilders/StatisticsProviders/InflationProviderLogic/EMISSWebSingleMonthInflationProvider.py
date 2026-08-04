import re
import pandas as pd
from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders import constants
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider


class EMISSWebSingleMonthInflationProvider(BaseSingleMonthInflationProvider):
    def __init__(self, path: Path):
        # year_to_col, region_to_row = self._getMapsVersion1(self.df)
        year_to_col, region_to_row = self._getMapsVersion2(path)
        self.year_to_col = year_to_col
        self.region_to_row = region_to_row

    def _getMapsVersion2(self, path):
        df = pd.read_excel(path, sheet_name=0, header=None, skiprows=[0, 1])
        self.df = df

        data_start_col = 2
        year_row = 0
        month_row = 1

        data_start_row = 3
        region_col = 0
        goodCategory_col = 1

        # Строим словарь: год -> номер колонки
        year_to_col = dict()
        curYear = None
        for col in range(data_start_col, len(df.columns)):
            year = df.iloc[year_row, col]
            if pd.notna(year):
                curYear = year

            month = df.iloc[month_row, col]

            val = f'{month.lower()} {curYear} г.'
            # dateVal = pd.to_datetime(val)
            dateVal = EMISSWebSingleMonthInflationProvider._parse_russian_date(val)

            if pd.notna(dateVal):
                try:
                    year_to_col[dateVal] = col
                except (ValueError, TypeError):
                    pass

        # Строим словарь: регион -> номер строки
        region_to_row = {}
        for row in range(data_start_row, len(self.df)):
            val = self.df.iloc[row, region_col]
            if pd.notna(val):
                region = str(val).strip()
                if region not in region_to_row:
                    region_to_row[region] = {'row': row, 'count': 1}
                else:
                    region_to_row[region]['count'] += 1

        regions = {}
        for k, v in region_to_row.items():
            if v['count'] == 1:
                regions[k] = v['row']

        currentRegion = None
        region_to_row = {}
        for row in range(data_start_row, len(self.df)):
            val = df.iloc[row, region_col]
            category = df.iloc[row, goodCategory_col]
            if pd.notna(val):
                currentRegion = str(val).strip()

            category = str(category).strip()

            key = f'{currentRegion}_{category}'
            region_to_row[key] = row

        return year_to_col, region_to_row

    def _getMapsVersion1(self, path):
        df = pd.read_excel(path, sheet_name=0, header=None, skiprows=[0])
        self.df = df

        data_start_col = 2
        year_row = 0
        data_start_row = 2
        region_col = 0

        # Строим словарь: год -> номер колонки
        year_to_col = dict()
        for col in range(data_start_col, len(df.columns)):
            val = df.iloc[year_row, col]
            # dateVal = pd.to_datetime(val)
            dateVal = EMISSWebSingleMonthInflationProvider._parse_russian_date(val)

            if pd.notna(dateVal):
                try:
                    year_to_col[dateVal] = col
                except (ValueError, TypeError):
                    pass

        # Строим словарь: регион -> номер строки
        region_to_row = {}
        for row in range(data_start_row, len(self.df)):
            val = self.df.iloc[row, region_col]
            if pd.notna(val):
                region = str(val).strip()
                if region not in region_to_row:
                    region_to_row[region] = {'row': row, 'count': 1}
                else:
                    region_to_row[region]['count'] += 1

        regions = {}
        for k, v in region_to_row.items():
            if v['count'] == 1:
                regions[k] = v['row']

        currentRegion = None
        region_to_row = {}
        for row in range(data_start_row, len(self.df)):
            val = df.iloc[row, region_col]
            if pd.notna(val):
                region = str(val).strip()

                if region in regions:
                    region_to_row[region] = row
                    currentRegion = region
                    continue

                key = f'{currentRegion}_{region}'
                region_to_row[key] = row

        return year_to_col, region_to_row

    @staticmethod
    def _parse_russian_date(date_str):
        """
        Парсинг русской даты в формате "месяц год г."
        """
        months = {
            'январь': 1, 'февраль': 2, 'март': 3,
            'апрель': 4, 'май': 5, 'июнь': 6,
            'июль': 7, 'август': 8, 'сентябрь': 9,
            'октябрь': 10, 'ноябрь': 11, 'декабрь': 12
        }

        # Ищем месяц и год
        pattern = r'([а-я]+)\s+(\d{4})'
        match = re.search(pattern, date_str.lower())

        if not match:
            quarterPattern = r'^\d{1}\s*кв.\s*\d{4}\s*г.$'
            m = re.match(quarterPattern, date_str.lower())
            if m:
                return None

            raise ValueError(f"Не удалось распарсить: {date_str}")

        month_name, year = match.groups()

        if month_name not in months:
            raise ValueError(f"Неизвестный месяц: {month_name}")

        return pd.Timestamp(year=int(year), month=months[month_name], day=1).date()
    def getInflation(self, region: str, product: str, d: date):
        column = self.year_to_col[d]

        region = self._updateRegionName(region, d)

        rowKey = f'{region}_{product}'
        if rowKey not in self.region_to_row:
            return None

        row = self.region_to_row[rowKey]
        print(f'Column = {column}, row = {row}, column key = {d}, row key = {rowKey}')

        value = float(self.df.iloc[row, column])
        return value

    def _updateRegionName(self, region: str, d: date):
        if region != constants.commonRegionName:
            return region

        if d < date(2023, 1, 1):
            return region

        return constants.commonRegionNameAlias
