from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseVariablesProvider import BaseVariablesProvider


class CompositeVariablesProvider(BaseVariablesProvider):
    def __init__(self, providers: list[BaseVariablesProvider]):
        self.providers = providers

    def getBaseVariables(self, configuration: str) -> list[str]:
        result = []
        for i in range(len(self.providers)):
            p = self.providers[i]
            result += p.getBaseVariables(configuration)

        return [x for x in set(result)]