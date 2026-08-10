from pathlib import Path

from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        ('mlcluster_qwen36_async_all_time', 'survey modelling (=true end of survey+1d), all data'),
        ('mlcluster_qwen36_async_all_time_week_before', 'survey modelling (=true end of survey-6d), all data'),
        ('mlcluster_qwen36_async_nousdrub_time_week_before', 'survey modelling (=true end of survey-6d), no usdrub')
]

models = {}
for folder, name in modellingResults:
        f = rootFolder/folder
        s = load_pdtable(f)
        s = aggregate_survey(s)

        models[name] = s

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName, 1)

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
        #show_date_labels=True,
        date_labels_for='all',
        use_intersection=True,
        title='Comparison of Expected 12m Inflation: True vs Models',
        figsize=(16, 8)
    )

viz.plot_correlation(
        variable='expected',
        save_path=Path('correlation_expected.png'),
        use_intersection=True,
)

viz.plot_correlation_diff(
        variable='expected',
        save_path=Path('correlation_expected.png'),
        use_intersection=True,
)