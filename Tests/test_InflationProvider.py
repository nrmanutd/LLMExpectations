from datetime import datetime
from unittest import TestCase

from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProvider import InflationProvider


class TestInflationProvider(TestCase):
    @classmethod
    def setUpClass(cls):
        """Метод вызывается ОДИН раз перед всеми тестами"""
        path = '../data/Inflation weekly by regions 2015 - 2026.xlsx'
        cls.inflationProvider = InflationProvider(path)

    def test_get_average_common_year_inflation_last_nmonth(self):
        format = '%d.%m.%Y'
        dates = ['01.01.2016', '01.01.2017', '01.09.2021', '01.07.2026', '01.06.2020']
        expectedValues = [(1 + 0.0077) ** 12 - 1, (1 + 0.004) ** 12 - 1, (1 + 0.0017) ** 12 - 1,
                          (1 + 0.0087) ** 12 - 1, (1 + 0.0027) ** 12 - 1]

        for i in range(len(dates)):
            inflation = self.inflationProvider.getAverageCommonYearInflationLastNMonth(
                datetime.strptime(dates[i], format), lastMonth=1)
            print(f'Expected: {expectedValues[i]}, actual: {inflation}')
            if expectedValues[i] is not None:
                assert abs(expectedValues[i] - inflation) < 0.00001
            else:
                assert inflation is None

    def test_get_average_regional_year_inflation_last_nmonth(self):
        format = '%d.%m.%Y'
        dates = ['01.01.2016', '01.01.2017', '01.09.2021', '01.07.2026', '01.06.2020']
        expectedValues = [(1 + 0.0064) ** 12 - 1, (1 + 0.0043) ** 12 - 1, (1 + 0.0032) ** 12 - 1,
                          (1 + 0.0056) ** 12 - 1, None]

        for i in range(len(dates)):
            inflation = self.inflationProvider.getAverageRegionalYearInflationLastNMonth(datetime.strptime(dates[i], format),
                                                                                    'Белгородская область', lastMonth=1)
            if expectedValues[i] is not None:
                assert abs(expectedValues[i] - inflation) < 0.00001
            else:
                assert inflation is None


    def test_get_average_regional_year_inflation_last_n_3_month(self):

        format = '%d.%m.%Y'
        dates = ['01.01.2016', '01.01.2017', '01.07.2026', '01.06.2020']
        expectedValues = [((1 + 0.0064) * (1 + 0.005) * (1 + 0.0083)) ** 4 - 1, ((1 + 0.0043) * (1+0.003) * (1 + 0.0014)) ** 4 - 1,
                          ((1 + 0.0056) * (1 + 0.003) * (1 + 0.0001)) ** 4 - 1, None]

        for i in range(len(dates)):
            inflation = self.inflationProvider.getAverageRegionalYearInflationLastNMonth(datetime.strptime(dates[i], format),
                                                                                    'Белгородская область', lastMonth=3)
            if expectedValues[i] is not None:
                assert abs(expectedValues[i] - inflation) < 0.00001
            else:
                assert inflation is None

    def test_get_products_common_year_inflation_last_nmonth(self):
        format = '%d.%m.%Y'
        dates = ['01.01.2023', '01.07.2026', '01.06.2020']
        expectedValues1 = [None, (1 + 0.0044) ** 12 - 1, None]
        expectedValues2 = [(1 + 0.0027) ** 12 - 1, (1 + 0.0076) ** 12 - 1, (1 + 0.0049)**12 - 1]
        products = ['Хлеб и хлебобулочные изделия (НД)', 'Хлеб пшеничный']

        for i in range(len(dates)):
            inflation = self.inflationProvider.getProductsCommonYearInflationLastNMonth(
                datetime.strptime(dates[i], format), products, lastMonth=1)

            if expectedValues1[i] is not None:
                assert abs(expectedValues1[i] - inflation[0]) < 0.00001
            else:
                assert inflation[0] is None

            if expectedValues2[i] is not None:
                assert abs(expectedValues2[i] - inflation[1]) < 0.00001
            else:
                assert inflation[1] is None

    def test_get_products_regional_year_inflation_last_nmonth(self):
        format = '%d.%m.%Y'
        dates = ['01.02.2023', '01.07.2026', '01.06.2020']
        expectedValues1 = [None, (100.24 * 99.04/10000) ** 6 - 1, None]
        expectedValues2 = [((100.68/100) *(99.13/100)) ** 6 - 1, (100.33*97.54/10000) ** 6 - 1, None]
        products = ['Хлеб и хлебобулочные изделия (НД)', 'Хлеб пшеничный']
        region = 'Республика Татарстан (Татарстан)'

        for i in range(len(dates)):
            inflation = self.inflationProvider.getProductsRegionalYearInflationLastNMonth(
                datetime.strptime(dates[i], format), region, products, lastMonth=2)

            if expectedValues1[i] is not None:
                assert abs(expectedValues1[i] - inflation[0]) < 0.00001
            else:
                assert inflation[0] is None

            print(f'Expected2: {expectedValues2[i]}, actual: {inflation[1]}')
            if expectedValues2[i] is not None:
                assert abs(expectedValues2[i] - inflation[1]) < 0.00001
            else:
                assert inflation[1] is None
