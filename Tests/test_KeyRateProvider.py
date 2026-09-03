from datetime import datetime
from pathlib import Path
from unittest import TestCase

from SurveyLogic.PromptBuilders.StatisticsProviders.KeyRateProvider import KeyRateProvider


class TestKeyRateProvider(TestCase):
    @classmethod
    def setUpClass(cls):
        """Метод вызывается ОДИН раз перед всеми тестами"""
        # path = Path('../data/Inflation weekly by regions 2015 - 2026.xlsx')
        path1 = Path('../data/cbr_key_rate_meetings_2013_2026.xlsx')

        keyRateProvider = KeyRateProvider(path1)
        cls.keyRateProvider = keyRateProvider

    def test_get_key_rate_increments(self):
        format = '%d.%m.%Y'
        dates = ['05.03.2022', '02.01.2009']
        expectedValues = [10.5, None]

        for i in range(len(dates)):
            keyRate = self.keyRateProvider.getKeyRateIncrements(datetime.strptime(dates[i], format).date(), 1)
            print(keyRate)
            if expectedValues[i] is None:
                assert len(keyRate) == 0
            else:
                assert abs(expectedValues[i] - keyRate[0]) < 0.000001

    def test_get_key_rate_increments_several(self):
        format = '%d.%m.%Y'
        dates = ['30.04.2022']
        expectedValues = [-3, -3, 0, 10.5]

        for i in range(len(dates)):
            keyRate = self.keyRateProvider.getKeyRateIncrements(datetime.strptime(dates[i], format).date(), 4)

            for j in range(len(expectedValues)):
                assert abs(expectedValues[j] - keyRate[j]) < 0.000001

    def test_get_key_rate_increments_from_future(self):
        format = '%d.%m.%Y'
        dates = ['25.07.2026']
        expectedValues = [-0.25, -0.25, -0.5]

        for i in range(len(dates)):
            keyRate = self.keyRateProvider.getKeyRateIncrements(datetime.strptime(dates[i], format).date(), 3)

            for j in range(len(expectedValues)):
                assert abs(expectedValues[j] - keyRate[j]) < 0.000001

    def test_get_key_rate_increments_from_beginning(self):
        format = '%d.%m.%Y'
        dates = ['14.09.2013']

        for i in range(len(dates)):
            keyRate = self.keyRateProvider.getKeyRateIncrements(datetime.strptime(dates[i], format).date(), 1)

            assert len(keyRate) == 0

    def test_get_key_rate_increments_from_future(self):
        format = '%d.%m.%Y'
        dates = ['15.10.2013']
        expectedValues = [0]

        for i in range(len(dates)):
            keyRate = self.keyRateProvider.getKeyRateIncrements(datetime.strptime(dates[i], format).date(), 3)

            for j in range(len(expectedValues)):
                assert abs(expectedValues[j] - keyRate[j]) < 0.000001

