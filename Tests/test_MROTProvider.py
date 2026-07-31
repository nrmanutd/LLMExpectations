from datetime import datetime
from unittest import TestCase

from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider


class TestMROTProvider(TestCase):
    def test_get_mrot(self):
        path = '../data/MROT_history.xlsx'
        mrotProvider = MROTProvider(path)
        format = '%d.%m.%Y'

        dates = ['31.12.1997', '01.01.1998', '01.01.2016', '06.06.2020', '01.07.2026']
        expectedValues = [83.49, 83.49, 5965, 12130, 27093]

        for i in range(len(dates)):
            mrot = mrotProvider.getMROT(datetime.strptime(dates[i], format))
            print(f'Expected = {expectedValues[i]}, actual = {mrot}')
            assert expectedValues[i] == mrot
