from SurveyResultsAnalysis.RegressionAnalysis.Learning.BaseVariablesProvider import BaseVariablesProvider
from SurveyResultsAnalysis.RegressionAnalysis.Learning.RegressionVariablesProvider import RegressionVariablesProvider


class AllVariablesProvider(BaseVariablesProvider):
    def __init__(self, isDelta, featuresMatrix):
        self.featuresMatrix = featuresMatrix
        self.regressionVariables = RegressionVariablesProvider(isDelta).getBaseVariables('')

    def getBaseVariables(self, configuration: str) -> list[str]:
        variables = self.regressionVariables
        row = self.featuresMatrix.loc[configuration]

        for col_name, value in row.items():
            if value != 'Да':
                continue

            if col_name == 'UsdRub':
                variables += [f'X1{i}' for i in range(1, 8)]

            if col_name == 'Inflation Total':
                variables += [f'X2{i}' for i in range(1, 5)]

            if col_name == 'Key Rate':
                variables += [f'X3{i}' for i in range(1, 4)]

            if col_name == 'Markers':
                variables += [f'X41{i:2.0f}' for i in range(11)]
                variables += [f'X42{i:2.0f}' for i in range(11)]

            if col_name == 'IE':
                variables.append('X51')

        print(f'{configuration}: {variables}')
        return variables