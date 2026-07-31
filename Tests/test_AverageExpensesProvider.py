from datetime import datetime
from unittest import TestCase

from SurveyLogic.PromptBuilders.StatisticsProviders.AverageExpensesProvider import AverageExpensesProvider


class TestAverageExpensesProvider(TestCase):
    def test_get_region_average_expenses(self):
        path = '../data/Average Buyings Regions 1980_2026.xlsx'
        format = '%d.%m.%Y'

        dates = ['31.12.1998', '01.01.1998', '01.01.2017', '06.06.2020', '01.07.2026']
        expectedValues = [5602.11, 5602.11, 201752, 215740, 401839]
        expensesProvider = AverageExpensesProvider(path)

        for i in range(len(dates)):
            mrot = expensesProvider.getRegionAverageExpenses('Белгородская область',
                                                             datetime.strptime(dates[i], format))
            assert expectedValues[i] == mrot

    def test_get_region_average_expenses_v2(self):
        path = '../data/Average Buyings Regions 1980_2026.xlsx'
        format = '%d.%m.%Y'

        dates = ['31.12.1998', '01.01.1998', '01.01.2017', '06.06.2020', '01.07.2026']
        expectedValues = [4880.25, 4880.25, 158448, 178319, 355846]
        expensesProvider = AverageExpensesProvider(path)

        for i in range(len(dates)):
            mrot = expensesProvider.getRegionAverageExpenses('Забайкальский край',
                                                             datetime.strptime(dates[i], format))
            assert expectedValues[i] == mrot
