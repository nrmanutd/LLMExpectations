from pathlib import Path

from SurveyExecutionTools.surveyExecutionHelpers import loadExperimentConfig, generate_filename_with_dates
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey, \
    generate_title_from_config

folder = Path('../data/SurveyResults/mlcluster_qwen36_async_only_usdrub_2022_02_04')
folder2 = Path('../data/SurveyResults/mlcluster_qwen36_async_hh_weekly_and_usdrub_2022_02_04')
folder3 = Path('../data/SurveyResults/mlcluster_qwen36_async_hh_weekly_nousdrub_2022_02_04')

cfg = loadExperimentConfig(folder/'configuration.txt')
fileName=generate_filename_with_dates(cfg)
title = generate_title_from_config(cfg, variable='expected', language='en')

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName)

surveys = load_pdtable(folder)
surveys2 = load_pdtable(folder2)
surveys3 = load_pdtable(folder3)

#surveys = load_pdtable_with_repeats(folder)

surveys = aggregate_survey(surveys)
surveys2 = aggregate_survey(surveys2)
surveys3 = aggregate_survey(surveys3)

models = {}
models['Only usdrub'] = surveys
models['Usdrub and expenses'] = surveys2
models['Only expenses'] = surveys3

# Создаем визуализатор
viz = TimeSeriesVisualizer(
        true_series=directEstimations,
        model_series=models
    )

# Строим график с кастомными цветами
colors = {
        'true': '#1F77B4',
        'Model A': '#FF6B6B',
        'Model B': '#4ECDC4',
        'Model C': '#FFE66D'
}

viz.plot_timeseries(
        variable='expected',
        colors=colors,
        show_date_labels=True,
        date_labels_for='true',
        use_intersection=True,
        title='Comparison of Observable Inflation: True vs Models',
        figsize=(16, 8)
    )