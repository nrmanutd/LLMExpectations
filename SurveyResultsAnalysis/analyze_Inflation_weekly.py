from pathlib import Path

from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_pdtable, aggregate_survey

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        ('mlcluster_qwen36_async_all_time', 'survey date+1day, all data')
]

models = {}
for folder, name in modellingResults:
        f = rootFolder/folder
        s = load_pdtable(f)
        s = aggregate_survey(s)

        models[name] = s

directEstimationsFileName = '../data/Direct_Inflation_Estimations_12m.xlsx'
directEstimations = load_from_official_statistics(directEstimationsFileName)

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
        date_labels_for='all',
        use_intersection=True,
        title='Comparison of Observable Inflation: True vs Models',
        figsize=(16, 8)
    )