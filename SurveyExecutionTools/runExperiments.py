import pandas as pd
from datetime import datetime, time

from SurveyLogic.PromptBuilders.StatisticsProviders.AverageExpensesProvider import AverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider

path = '../data/Inflation weekly by regions 2015 - 2026.xlsx'
format = '%d.%m.%Y'

df = pd.read_excel(path, sheet_name=0, header=None, skiprows=[0])
print(df)
print(df.columns)

dates = ['31.12.1998', '01.01.1998', '01.01.2017', '06.06.2020', '01.07.2026', '01.07.2027']
expectedValues = [5602.11, 5602.11, 201752, 215740, 401839]
expensesProvider = AverageExpensesProvider(path)

for i in range(len(dates)):
    mrot = expensesProvider.getRegionAverageExpenses('Белгородская область', datetime.strptime(dates[i], format))
    print(f'expected: {expectedValues[i]}, actual: {mrot}')