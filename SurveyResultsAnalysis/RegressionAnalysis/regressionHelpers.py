import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from SurveyResultsAnalysis.RegressionAnalysis.Learning.ARLearner import ARLearner
from SurveyResultsAnalysis.RegressionAnalysis.Learning.AllVariablesProvider import AllVariablesProvider
from SurveyResultsAnalysis.RegressionAnalysis.Learning.ElasticNetLearner import ElasticNetLearner
from SurveyResultsAnalysis.RegressionAnalysis.Learning.RegressionVariablesProvider import RegressionVariablesProvider
from SurveyResultsAnalysis.RegressionAnalysis.Learning.RidgeLearner import RidgeLearner
from SurveyResultsAnalysis.RegressionAnalysis.Learning.XGBoostLearner import XGBoostLearner
from SurveyResultsAnalysis.helpers import load_pdtable, aggregate_survey


def _load_one(rootFolder: Path, folder: str, name: str):
    f = rootFolder / folder
    s = load_pdtable(f)
    s = aggregate_survey(s)
    s.to_excel('survey.xlsx')
    return name, s

def loadSurveyResults(rootFolder: Path, surveyResults, max_workers: int = 12):
    models = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(_load_one, rootFolder, folder, name)
            for folder, name in surveyResults
        ]
        for fut in as_completed(futures):
            name, s = fut.result()   # дождались — пишем в общий dict
            models[name] = s
    return models

def getSurveyVisualization(predictions, dates):
    result_df = pd.DataFrame({
        'exp_mean': predictions.values
    }, index=dates)

    # Переименовываем индекс в 'date' для ясности (опционально)
    result_df.index.name = 'date'
    return result_df


def getLearner(isDelta: bool, isDummy: bool, featuresMatrix, learnerType: str):
    if learnerType == 'XGBoost':
        variablesProvider = AllVariablesProvider(isDelta, featuresMatrix)
        learner = XGBoostLearner(isDummy)
    elif 'AR(' in learnerType:
        p = int(learnerType.replace('AR(', '').replace(')', ''))
        if p > 6:
            raise ValueError(f'p for AR(p) should be <= 6, instead: {p}')

        variablesProvider = RegressionVariablesProvider(isDelta, p)
        learner = ARLearner(isDummy, p)
    elif learnerType == 'Elastic Net':
        variablesProvider = AllVariablesProvider(isDelta, featuresMatrix)
        learner = ElasticNetLearner(isDummy)
    elif learnerType == 'Ridge':
        variablesProvider = AllVariablesProvider(isDelta, featuresMatrix)
        learner = RidgeLearner(isDummy)
    else:
        raise ValueError(f'Incorrect learner type {learnerType}')

    return variablesProvider, learner