from pathlib import Path

import numpy as np

from Configuration import visualizationConfiguration
from SurveyLogic.PromptBuilders.StatisticsProviders.KeyRateProvider import KeyRateProvider
from SurveyResultsAnalysis.RegressionAnalysis.ForecastRobustness import ForecastRobustness
from SurveyResultsAnalysis.RegressionAnalysis.RegressionVisualizer import RegressionVisualizer
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults, getSurveyVisualization
from SurveyResultsAnalysis.TimeSeriesVisualizer import TimeSeriesVisualizer
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_official_inflation, \
    load_official_analytics_expectation, load_usdrub

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        #('mlcluster_qwen38_async_all_prevexp_-6d', 'QWEN 3.8 (все данные + IE - markers, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_time', 'QWEN 3.6 (все данные, в день Инфом)'),
        #('mlcluster_qwen36_async_all_time_week_before', 'QWEN 3.6 (все данные, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_two_weekbefore', 'QWEN 3.6 (все данные, -2w от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time_week_before', 'QWEN 3.6 (без usdrub, -7d от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time', 'QWEN 3.6 (без usdrub, в день Инфом)'),
        #('mlcluster_qwen36_async_norlms_weekbefore', 'QWEN 3.6 (без RLMS, -7d от Инфом)'),
        #('mlcluster_qwen36_async_only_rlms_-1week', 'QWEN 3.6 (только RLMS, -7d от Инфом)'),
        #('mlcluster_qwen38_async_no_rlms_prevexp_-6d', 'QWEN 3.8 (без RLMS + IE - markers, -7d от Инфом)'),
        #('mlcluster_qwen38_async_no_goods_no_previous_ie_prevexp_-6d', 'QWEN 3.8 (RLMS pass - markers - IE - , -7d от Инфом)'),
        #('mlcluster_qwen38_async_no_rlms_-6d', 'QWEN 3.8 (без RLMS без IE без маркеров + общ инфо, -7d от Инфом'),
        #('mlcluster_qwen38_async_norlms_noIE_keyrate_-6d', 'QWEN 3.8 (без RLMS без IE + ключ, -7d от Инфом)'),
        #('mlcluster_qwen36_async_rlms_pass_noIE_keyrate_-6d', 'QWEN 3.8 (RLMS pass -IE + ключ, -7d от Инфом)'),
        #('mlcluster_qwen36_async_rlms_pass_noIE_keyrate_news_-6d', 'QWEN 3.8 (news + RLMS pass -IE + ключ, -7d от Инфом)'),
        #('mlcluster_qwen36_async_no_rlms_pass_noIE_keyrate_news_-6d', 'QWEN 3.8 (news - RLMS - IE + ключ, 7d от Инфом)'),
        #('mlcluster_qwen36_async_rlms_expenses_noIE_keyrate_news_-6d', 'QWEN 3.8 (news + RLMS e - IE + ключ, 7d от Инфом)'),
        #('mlcluster_qwen36_async_norlms_pass_noIE_nokeyrate_-6d', 'QWEN 3.8 (news + RLMS e - IE - ключ, 7d от Инфом)'),
        #('mlcluster_qwen38_async_norlms_pass_noIE_nokeyrate_nonews_-6d', 'QWEN 3.8 (RLMS e -news -IE -ключ, 7d от Инфом)'),
        #('mlcluster_qwen38_async_norlms_noIE_nokeyrate_-6d', 'QWEN 3.8 (-RLMS +news -IE -ключ, 7d от Инфом)'),
        #('mlcluster_qwen38_async_rlmse_news_nomarkers_-6d', 'QWEN 3.8 (+RLMS e +news -markers, 7d)'),
        ('mlcluster_qwen38_async_news_rlmse_reginf_-6d', 'QWEN 3.8 (+RLMS e +news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_news_rlmsfull_reginf_-6d', 'QWEN 3.8 (+RLMS full  +news +reg inf, 7d)')
]

isDelta = False
isOOS = True
isFWL = False
isExpandingOOS = True
nMonth = 6
OOSStartPoints = 30

#datesToFilter = {np.datetime64('2022-04-02')}
datesToFilter = set[np.datetime64]()
#datesToExclude = (np.datetime64('2022-02-23'), np.datetime64('2022-06-01'))
datesToExclude = (np.datetime64('2022-01-01'), np.datetime64('2027-02-01'))
#datesToExclude = (np.datetime64('2027-02-23'), np.datetime64('2027-06-01'))
datesToInclude = (np.datetime64('2000-01-01'), np.datetime64('2030-07-01'))

threshold = 20

surveyResults = loadSurveyResults(rootFolder, modellingResults)

keyRateProvider = KeyRateProvider(visualizationConfiguration.keyRatePath)
directEstimations = load_from_official_statistics(visualizationConfiguration.directInflationEstimationsPath, 1)
officialInflation = load_official_inflation(visualizationConfiguration.officialInflationPath)
usdrubRate = load_usdrub(visualizationConfiguration.usdrubPath)
surveyRegressionService = SurveyRegressionService(directEstimations, officialInflation, usdrubRate, keyRateProvider, datesToFilter, datesToExclude, datesToInclude)
visualizer = RegressionVisualizer()

visualizationResults = {}
errors = []

if isDelta:
    if isFWL:
        variables = {'dY: X2=I-12m(t), X4=UsdRub, X5=delta IE (t-1)': (['X2', 'X4', 'X5', 'X6'], 'X3'), 'dLLM: X2=I-12m(t), X4=UsdRub, X5=delta IE (t-1)': (['X2', 'X4', 'X5', 'X6'], 'Y')}
    else:
        #variables = {'X2=I-12m(t), X3=LLM_IE(t), X4=UsdRub, X5=delta IE (t-1)':(['X2', 'X3', 'X4', 'X5'],'Y'), 'X2=I-12m(t), X4=UsdRub, X5=delta IE (t-1)': (['X2', 'X4', 'X5'], 'Y'), 'X5=dIE(t-1)':(['X5'], 'Y'), 'X3=dLLM_IE(t-1)':(['X3'], 'Y')}
        variables = {'X5=dIE-12m(t-1), X3=dLLM_IE(t)': (['X5', 'X3'], 'Y'), 'X5=dIE-12m(t-1)': (['X5'], 'Y'), }
        #variables = {'X5=dIE-12m(t)': (['X5'], 'Y')}
else:
    if isFWL:
        variables = {'X1=IE, X2=I-12m(t), X3=LLM_IE(t)': (['X1', 'X2', 'X4', 'X6'], 'X3'),
                     'X1=IE, X2=I-12m(t)': (['X1', 'X2', 'X4', 'X6'], 'Y')}
    else:
        variables = {'X1=IE, X3=LLM_IE(t)': (['X1', 'X3'], 'Y'), 'X1=IE': (['X1'], 'Y')}
        #variables = {'X1=IE, X2=I-12m(t), X3=LLM_IE(t)': (['X1', 'X2', 'X3', 'X4'], 'Y'), 'X1=IE, X2=I-12m(t)': (['X1', 'X2', 'X4'], 'Y')}
        #variables = {'X1=IE, X3=LLM_IE(t)': (['X1', 'X3'], 'Y'), 'X1=IE': (['X1'], 'Y')}
        #variables = {'X3=LLM_IE(t)': (['X3'], 'Y'), 'X1=IE, X3=LLM_IE(t)': (['X1', 'X3'], 'Y')}
        #variables = {'X1=IE, X3=LLM_IE(t)': (['X1', 'X3'], 'Y')}


postfix = f'{'OOS' if isOOS else ''}_{'delta' if isDelta else ''}'
trainedModels = []

for vn, v in variables.items():
    regressionResults = {}
    prefix = vn

    for name, survey in surveyResults.items():
        if isOOS:
            if isExpandingOOS:
                y, r, m, dates = surveyRegressionService.fit_oos(survey, v, isDelta=isDelta, nMonth=nMonth, start_n=OOSStartPoints)
            else:
                y, r, m, dates = surveyRegressionService.fit_oos_fixedsplit(survey, v, isDelta=isDelta, nMonth=nMonth)
        else:
            y, r, m, dates = surveyRegressionService.fit(survey, v, isDelta=isDelta, nMonth=nMonth)

        trainedModels.append(m)
        surveyRegressionService.estimateCorr(survey)
        errors.append((y - r))

        regressionResults[name] = (y, r, m)
        visualizationResults[f'Прогноз {prefix} {name}'] = getSurveyVisualization(r, dates)

    visualizer.visualize(regressionResults, save_path=f'{prefix}_regression_{postfix}.png', additional_title=prefix)

for i in range(len(modellingResults)):
    print(f'Model: {modellingResults[i][1]}, errors: {len(errors)}, models: {len(modellingResults)}')
    e_base = errors[i + len(modellingResults)]
    e_llm = errors[i]

    #model_macro_base = trainedModels[i + len(modellingResults)]
    #model_macro_llm = trainedModels[i]

    #partial_r2_llm = (model_macro_base.ssr - model_macro_llm.ssr) / model_macro_base.ssr
    #print(f'Partial R^2: {partial_r2_llm}')

    visualizer.plot_llm_oos_gain(e_base, e_llm, modellingResults[i][1], threshold=threshold)
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

#viz.plot_timeseries(
#        variable='expected',
#        colors=colors,
#        xlabel='Дата',
#        ylabel='Инфляция, %',
#        show_date_labels=True,
#        date_labels_for='true',
#        title='Ожидаемая на год вперед инфляция: моделирование vs реальный опрос',
#        figsize=(16, 8),
#        label_offset_y=-0.1,
#        label_offset_x=0,
#        save_path=Path(f'timeseries_regression_{postfix}.png')
#    )