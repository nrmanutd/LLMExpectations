from pathlib import Path

from Configuration import visualizationConfiguration
from SurveyResultsAnalysis.RegressionAnalysis.RegressionVisualizer import RegressionVisualizer
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_official_inflation

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        ('mlcluster_qwen36_async_all_time', 'QWEN 3.6 (все данные, в день Инфом)'),
        ('mlcluster_qwen36_async_all_time_week_before', 'QWEN 3.6 (все данные, -7d от Инфом)'),
        ('mlcluster_qwen36_async_all_two_weekbefore', 'QWEN 3.6 (все данные, -2w от Инфом)'),
        ('mlcluster_qwen36_async_nousdrub_time_week_before', 'QWEN 3.6 (без usdrub, -7d от Инфом)'),
        ('mlcluster_qwen36_async_nousdrub_time', 'QWEN 3.6 (без usdrub, в день Инфом)'),
        ('mlcluster_qwen36_async_norlms_weekbefore', 'QWEN 3.6 (без RLMS, -7d от Инфом)')
]

surveyResults = loadSurveyResults(rootFolder, modellingResults)

directEstimations = load_from_official_statistics(visualizationConfiguration.directInflationEstimationsPath, 1)
officialInflation = load_official_inflation(visualizationConfiguration.officialInflationPath)

print(directEstimations)
print(officialInflation)

surveyRegressionService = SurveyRegressionService(directEstimations, officialInflation)

regressionResults = {}
for name, survey in surveyResults.items():
    y, r, m = surveyRegressionService.fit(survey)
    regressionResults[name] = (y, r, m)

visualizer = RegressionVisualizer()
visualizer.visualize(regressionResults, save_path='regression.png')