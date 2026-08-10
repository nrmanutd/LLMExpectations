from datetime import datetime
from pathlib import Path
from unittest import TestCase

from SurveyLogic.PromptBuilders.StatisticsProviders.USDRUBRateProvider import USDRUBRateProvider

class TestUSDRUBRateProvider(TestCase):
    @classmethod
    def setUpClass(cls):
        """Метод вызывается ОДИН раз перед всеми тестами"""
        # path = Path('../data/Inflation weekly by regions 2015 - 2026.xlsx')
        path1 = Path('../data/RC_F01_01_2009_T01_08_2026.xlsx')

        usdrubRateProvider = USDRUBRateProvider(path1)
        cls.rateProvider = usdrubRateProvider

    def test_get_rate_difference_by_month_offset(self):
        format = '%d.%m.%Y'
        dates = ['05.03.2022', '02.01.2009']
        expectedValues = [(111.7564/76.6501 - 1), None]

        for i in range(len(dates)):
            rateChange = self.rateProvider.getRateDifferenceByMonthOffset(datetime.strptime(dates[i], format).date(), 1)
            if expectedValues[i] is None:
                assert rateChange is None
            else:
                assert abs(expectedValues[i] - rateChange) < 0.000001

    def test_get_rate_difference_by_weeks_offset(self):
        format = '%d.%m.%Y'
        dates = ['04.03.2022', '02.01.2009']
        expectedValues = [(103.2487 / 80.4194 - 1), None]

        for i in range(len(dates)):
            rateChange = self.rateProvider.getRateDifferenceByWeeksOffset(datetime.strptime(dates[i], format).date(), 1)
            if expectedValues[i] is None:
                assert rateChange is None
            else:
                assert abs(expectedValues[i] - rateChange) < 0.000001

    def test_get_rate_difference_by_days_offset(self):
        format = '%d.%m.%Y'
        dates = ['04.03.2022', '13.01.2009', '02.01.2009']
        expectedValues = [(103.2487 / 91.7457 - 1), (30.5331/29.3916 - 1), None]

        for i in range(len(dates)):
            rateChange = self.rateProvider.getRateDifferenceByDaysOffset(datetime.strptime(dates[i], format).date(), 1)
            print(f'{dates[i]}, expected: {expectedValues[i]}, actual: {rateChange}')
            if expectedValues[i] is None:
                assert rateChange is None
            else:
                assert abs(expectedValues[i] - rateChange) < 0.000001
