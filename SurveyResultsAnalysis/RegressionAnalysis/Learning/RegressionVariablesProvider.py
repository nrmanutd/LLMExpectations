from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseVariablesProvider import BaseVariablesProvider


class RegressionVariablesProvider(BaseVariablesProvider):
    def __init__(self, isDelta: bool):
        self.isDelta = isDelta

    def getBaseVariables(self, configuration: str) -> list[str]:
        return ['X5'] if self.isDelta else ['X1']