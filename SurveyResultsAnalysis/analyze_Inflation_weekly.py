import pandas as pd

from SurveyResultsAnalysis.DualTimeSeriesPlotter import DualTimeSeriesPlotter
from SurveyResultsAnalysis.InflationComparisonAnalyzer import InflationComparisonAnalyzer
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey, \
    load_pdtable_with_repeats

folder = '../data/SurveyResults/mlcluster_qwen36_async_hh_weekly_2022_02_04'

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName)
print(directEstimations.head())

surveys = load_pdtable(folder)
#surveys = load_pdtable_with_repeats(folder)

surveys = aggregate_survey(surveys)

analyzer = TimeSeriesVisualizer(directEstimations, surveys)
analyzer.plot_both(save_prefix='both_series')