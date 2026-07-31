from abc import ABC
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd


class MROTProvider(ABC):

    def __init__(self, excel_file_path: Path):
        df = pd.read_excel(excel_file_path, sheet_name=1, header=None)

        # Первая строка - даты, вторая строка - числа
        self.dates = df.iloc[0].dropna().values
        self.values = df.iloc[1].dropna().values

        # Преобразуем даты в datetime объекты
        self.dates = pd.to_datetime(self.dates)

        # Сортируем по датам (на всякий случай)
        sorted_indices = np.argsort(self.dates)
        self.dates = self.dates[sorted_indices]
        self.values = self.values[sorted_indices]

        # Создаем словарь для быстрого доступа
        self.date_to_value = dict(zip(self.dates, self.values))

    def getMROT(self, d: date) -> float:

        mask = self.dates < d
        valid_dates = self.dates[mask]

        if len(valid_dates) == 0:
            return self.values[0]

        closest_date = valid_dates[-1]
        return self.date_to_value[closest_date]
