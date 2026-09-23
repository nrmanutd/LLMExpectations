from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseVariablesProvider import BaseVariablesProvider


class RegressionVariablesProvider(BaseVariablesProvider):
    def __init__(self, isDelta: bool, p: int):
        self.p = p
        self.isDelta = isDelta

    def getBaseVariables(self, configuration: str) -> list[str]:
        return [f'X05{i}' for i in range(1, self.p + 1)] if self.isDelta else [f'X0{i}' for i in range(1, self.p + 1)]