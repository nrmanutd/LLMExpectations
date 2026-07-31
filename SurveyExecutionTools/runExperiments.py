from datetime import datetime

import pandas as pd

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProvider import InflationProvider

path = '../data/Inflation weekly by regions 2015 - 2026.xlsx'
format = '%d.%m.%Y'
inflationProvider = InflationProvider(path)