from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseVariablesProvider import BaseVariablesProvider
from SurveyResultsAnalysis.RegressionAnalysis.Learning.RegressionVariablesProvider import RegressionVariablesProvider


class AllVariablesProvider(BaseVariablesProvider):
    def __init__(self, isDelta, featuresMatrix):
        self.featuresMatrix = featuresMatrix
        self.regressionVariables = RegressionVariablesProvider(isDelta).getBaseVariables()

    def getBaseVariables(self, configuration: str) -> list[str]:
        vars = self.regressionVariables

        print(self.featuresMatrix)

        return vars