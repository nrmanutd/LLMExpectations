import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.BaseSurveyRegressionService import BaseSurveyRegressionService


class MultipleSurveyRegressionService(BaseSurveyRegressionService):
    def __init__(self, service: BaseSurveyRegressionService):
        self.service = service

    def fitBaseVariablesWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1,
                                   cutoff_date: np.datetime64 | None = None, train_share: float = 0.8):
        return self.service.fitBaseVariablesWithConfig(survey[0], v, isOOS, isExpandingOOS, cutoff_date=cutoff_date, nMonth=nMonth, train_share=train_share)

    def fitWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1,
                      cutoff_date: np.datetime64 | None = None, train_share: float = 0.8):

        resultY = None
        resultR = None
        resultTM = None
        resultDates = None

        for i in range(len(survey)):
            print(f'Fitting multiple average for survey #{i}...')
            curSurvey = survey[i]

            ty, tr, tm, tdates = self.service.fitWithConfig(
                curSurvey, v, isOOS, isExpandingOOS,
                cutoff_date=cutoff_date, nMonth=nMonth, train_share=train_share)

            if i == 0:
                resultY = ty
                resultR = tr
                resultTM = tm
                resultDates = tdates
            else:
                resultR += tr

        print('All surveys are fitted')

        resultR = resultR / len(survey)
        return resultY, resultR, resultTM, resultDates