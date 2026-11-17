from datetime import date, datetime

import pandas as pd
from pathlib import Path

from SurveyLogic.PromptBuilders.StatisticsProviders.BaseKeyRateProvider import BaseKeyRateProvider


class KeyRateProvider(BaseKeyRateProvider):
    def __init__(self, path: Path):
        self.df = self._load(path)

    def getKeyRateIncrements(self, d: date, lastN: int = 1) -> list[float]:
        result = []

        df = self.df
        dt = datetime.combine(d, datetime.min.time())
        past_dates = df.index[df.index < dt]

        if len(past_dates) == 0:
            return []  # нет данных в прошлом

        # Берем самую позднюю дату из прошлого
        found_date = past_dates[-1]
        current_idx = df.index.get_loc(found_date)

        for i in range(lastN):
            curIdx = current_idx - i
            prevIdx = curIdx - 1

            if prevIdx < 0:
                return result

            delta = df.iloc[curIdx, 0] - df.iloc[prevIdx, 0]
            result.append(delta)

        return result

    def _load(self, path: Path):
        df = pd.read_excel(path, header=0, decimal=',')
        df = df.set_index('Дата заседания')
        df.sort_index(inplace=True)

        df['KeyRate'] = df['Новое значение ставки, %'].astype(float)

        return df