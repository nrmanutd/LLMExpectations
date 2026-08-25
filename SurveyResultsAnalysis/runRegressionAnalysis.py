from pathlib import Path

from Configuration import visualizationConfiguration
from SurveyResultsAnalysis.RegressionAnalysis.RegressionVisualizer import RegressionVisualizer
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults, getSurveyVisualization
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_official_inflation, \
    load_official_analytics_expectation

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        ('mlcluster_qwen36_async_all_time', 'QWEN 3.6 (все данные, в день Инфом)'),
        ('mlcluster_qwen36_async_all_time_week_before', 'QWEN 3.6 (все данные, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_two_weekbefore', 'QWEN 3.6 (все данные, -2w от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time_week_before', 'QWEN 3.6 (без usdrub, -7d от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time', 'QWEN 3.6 (без usdrub, в день Инфом)'),
        #('mlcluster_qwen36_async_norlms_weekbefore', 'QWEN 3.6 (без RLMS, -7d от Инфом)')
]

surveyResults = loadSurveyResults(rootFolder, modellingResults)

directEstimations = load_from_official_statistics(visualizationConfiguration.directInflationEstimationsPath, 1)
officialInflation = load_official_inflation(visualizationConfiguration.officialInflationPath)
surveyRegressionService = SurveyRegressionService(directEstimations, officialInflation)
visualizer = RegressionVisualizer()

visualizationResults = {}
variables = [['X1', 'X2', 'X3'], ['X1', 'X2'], ['X2', 'X3']]
for v in variables:
    regressionResults = {}
    prefix = '_'.join(v)

    for name, survey in surveyResults.items():
        survey.to_excel(f'{name}.xlsx')
        y, r, m, dates = surveyRegressionService.fit(survey)
        regressionResults[name] = (y, r, m)
        visualizationResults[f'Прогноз {prefix} {name}'] = getSurveyVisualization(r, dates)

    visualizer.visualize(regressionResults, save_path=f'{prefix}_regression.png')

keyDates = {'15.12.2014': 'Черный понедельник', '31.01.2020': 'COVID-19 в РФ', '24.02.2022': 'Начало СВО', '18.06.2026': 'НПЗ в Московской области', '01.05.2018': 'Топливный кризис в РФ'}

analytics = load_official_analytics_expectation(visualizationConfiguration.analyticsForecastPath, visualizationConfiguration.analyticsDatesMapPath)
viz = TimeSeriesVisualizer(
        true_series=directEstimations,
        model_series=visualizationResults,
        additional_series={'Инфляция Росстат (г/г)': officialInflation, 'Опрос аналитиков (на дек.)':analytics},
        vertical_lines=keyDates
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
        xlabel='Дата',
        ylabel='Инфляция, %',
        show_date_labels=True,
        date_labels_for='true',
        title='Ожидаемая на год вперед инфляция: моделирование vs реальный опрос',
        figsize=(16, 8),
        label_offset_y=-0.1,
        label_offset_x=0,
        save_path=Path('timeseries_regression.png')
    )