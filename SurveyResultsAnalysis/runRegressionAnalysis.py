from pathlib import Path

import numpy as np

from Configuration import visualizationConfiguration
from SurveyResultsAnalysis.RegressionAnalysis.ForecastRobustness import ForecastRobustness
from SurveyResultsAnalysis.RegressionAnalysis.RegressionVisualizer import RegressionVisualizer
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults, getSurveyVisualization
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_official_inflation, \
    load_official_analytics_expectation, load_usdrub

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        #('mlcluster_qwen38_async_all_prevexp_-6d', 'QWEN 3.8 (все данные, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_time', 'QWEN 3.6 (все данные, в день Инфом)'),
        #('mlcluster_qwen36_async_all_time_week_before', 'QWEN 3.6 (все данные, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_two_weekbefore', 'QWEN 3.6 (все данные, -2w от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time_week_before', 'QWEN 3.6 (без usdrub, -7d от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time', 'QWEN 3.6 (без usdrub, в день Инфом)'),
        ('mlcluster_qwen36_async_norlms_weekbefore', 'QWEN 3.6 (без RLMS, -7d от Инфом)'),
        #('mlcluster_qwen36_async_only_rlms_-1week', 'QWEN 3.6 (только RLMS, -7d от Инфом)'),
        #('mlcluster_qwen38_async_no_rlms_prevexp_-6d', 'QWEN 3.8 (без RLMS, -7d от Инфом)'),
        #('mlcluster_qwen38_async_no_goods_no_previous_ie_prevexp_-6d', 'QWEN 3.8 (RLMS паспорт + общ инфо, -7d от Инфом)'),
        ('mlcluster_qwen38_async_no_rlms_-6d', 'QWEN 3.8 (без RLMS без IE без маркеров + общ инфо, -7d от Инфом'),
        ('mlcluster_qwen36_async_norlms_noIE_keyrate_-6d', 'QWEN 3.8 (без RLMS без IE + ключ, -7d от Инфом)')
]

#datesToFilter = {np.datetime64('2022-04-02')}
datesToFilter = set[np.datetime64]()
threshold = 6

surveyResults = loadSurveyResults(rootFolder, modellingResults)

directEstimations = load_from_official_statistics(visualizationConfiguration.directInflationEstimationsPath, 1)
officialInflation = load_official_inflation(visualizationConfiguration.officialInflationPath)
usdrubRate = load_usdrub(visualizationConfiguration.usdrubPath)
surveyRegressionService = SurveyRegressionService(directEstimations, officialInflation, usdrubRate, datesToFilter)
visualizer = RegressionVisualizer()

visualizationResults = {}
errors = []
isDelta = True
isOOS = True

#variables = {'X1=UsdRub, X2=I-12m(t), X3=LLM_IE(t)': ['X1', 'X2', 'X3'], 'X1=UsdRub, X2=I-12m(t)': ['X1', 'X2'], 'X2=I-12m(t), X3=LLM_IE(t)': ['X2', 'X3']}
variables = {'X2=I-12m(t), X3=LLM_IE(t), X4=UsdRub, X5=delta IE (t-1)':['X2', 'X3', 'X4', 'X5'], 'X2=I-12m(t), X4=UsdRub, X5=delta IE (t-1)': ['X2', 'X4', 'X5']}

postfix = f'{'OOS' if isOOS else ''}_{'delta' if isDelta else ''}'

for vn, v in variables.items():
    regressionResults = {}
    prefix = vn

    for name, survey in surveyResults.items():
        if isOOS:
            y, r, m, dates = surveyRegressionService.fit_oos(survey, v, isDelta=isDelta)
        else:
            y, r, m, dates = surveyRegressionService.fit(survey, v, isDelta=isDelta)

        surveyRegressionService.estimateCorr(survey)
        errors.append((y - r))

        regressionResults[name] = (y, r, m)
        visualizationResults[f'Прогноз {prefix} {name}'] = getSurveyVisualization(r, dates)

    visualizer.visualize(regressionResults, save_path=f'{prefix}_regression_{postfix}.png', additional_title=prefix)

for i in range(len(modellingResults)):
    print(f'Model: {modellingResults[i][1]}')
    e_base = errors[i + len(modellingResults)]
    e_llm = errors[i]
    visualizer.plot_llm_oos_gain(e_base, e_llm, modellingResults[i][0], threshold=threshold)
    fr = ForecastRobustness(e_llm, e_base)
    fr.print_robustness_report(block_size=4, n_boot=10_000, hac_lags=3)

for k, v in surveyResults.items():
    visualizationResults[k] = v

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
        save_path=Path(f'timeseries_regression_{postfix}.png')
    )