from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService


class CachingSurveyRegressionService:
    def __init__(self, surveyRegressionService: SurveyRegressionService):
        self.surveyRegressionService = surveyRegressionService
        self.cache = {}

    def fitWithConfig(self, survey, v, isOOS: bool, isExpandingOOS: bool, nMonth: int = 1, start_n: int = 30, train_share: float = 0.8):
        key = '_'.join(v[0])
        key = f'{key}_{v[1]}_{isOOS}_{isExpandingOOS}_{nMonth}_{start_n}_{train_share}'

        if key in self.cache:
            return self.cache[key]

        result = self.surveyRegressionService.fitWithConfig(survey, v, isOOS, isExpandingOOS, nMonth, start_n, train_share)
        self.cache[key] = result

        return result