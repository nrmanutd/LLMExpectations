from pathlib import Path

import pandas as pd

from SurveyExecutionTools.surveyExecutionHelpers import loadExperimentConfig, generate_filename_with_dates
from SurveyResultsAnalysis.DualTimeSeriesPlotter import DualTimeSeriesPlotter
from SurveyResultsAnalysis.InflationComparisonAnalyzer import InflationComparisonAnalyzer
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey, \
    load_pdtable_with_repeats, generate_title_from_config

folder = Path('../data/SurveyResults/mlcluster_qwen36_async_only_usdrub_2022_02_04')

cfg = loadExperimentConfig(folder/'configuration.txt')
fileName=generate_filename_with_dates(cfg)
title = generate_title_from_config(cfg, variable='expected', language='en')

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName)
print(directEstimations.head())

surveys = load_pdtable(folder)
#surveys = load_pdtable_with_repeats(folder)

surveys = aggregate_survey(surveys)

analyzer = TimeSeriesVisualizer(directEstimations, surveys)
#analyzer.plot_both(save_prefix='both_series',use_intersection=True)

analyzer.plot_timeseries(
    variable='expected',
    title=title,
    use_intersection=True,
    show_date_labels=True,
    date_labels_for='both',
    save_path=folder/fileName
)