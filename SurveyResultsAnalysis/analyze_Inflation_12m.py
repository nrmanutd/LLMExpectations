
from SurveyResultsAnalysis.InflationComparisonAnalyzer import InflationComparisonAnalyzer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey

folder = '../data/SurveyResults/mlcluster_qwen36_custom_inflation_politics_2016_2026_QS'

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName)
print(directEstimations.head())

surveys = load_pdtable(folder)
surveys = aggregate_survey(surveys)

analyzer = InflationComparisonAnalyzer(directEstimations, surveys)
analyzer.analyze()
analyzer.print_summary()
analyzer.plot_all()
analyzer.export_results()