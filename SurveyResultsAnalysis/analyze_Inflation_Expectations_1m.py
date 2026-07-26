import pandas as pd
from SurveyResultsAnalysis.PercentagesAnalyzer import PercentagesAnalyzer
from SurveyResultsAnalysis.helpers import load_pdtable, load_from_official_statistics_1m, aggregate_to_percentages

categories = [
    'вырастут очень сильно',
    'вырастут умеренно',
    'вырастут незначительно',
    'не изменятся',
    'снизятся',
    'затрудняюсь ответить'
]

folder = '../data/SurveyResults/mlcluster_qwen36_custom_inflation_politics_2016_2026_QS'

quarterly_agg_df = load_pdtable(folder)
quarterly_agg_df = aggregate_to_percentages(quarterly_agg_df, date_col='date', response_col='expected_1m')
print(quarterly_agg_df.head())

directEstimationsFileName = '../data/Expected_Inflation_1m.xlsx'
monthly_df = load_from_official_statistics_1m(directEstimationsFileName)
print(monthly_df.head())

# Создаем анализатор
analyzer = PercentagesAnalyzer(monthly_df, quarterly_agg_df, categories)

# Получаем результаты
summary = analyzer.get_summary()
print("Сводка по всем датам:")
print(summary)

# Постройте графики
analyzer.plot_all(save_prefix='expectations_1m')