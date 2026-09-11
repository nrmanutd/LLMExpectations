import math
import time
from pathlib import Path

import numpy as np

from Configuration import visualizationConfiguration
from SurveyLogic.PromptBuilders.StatisticsProviders.KeyRateProvider import KeyRateProvider
from SurveyResultsAnalysis.RegressionAnalysis.ForecastRobustness import ForecastRobustness
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults
from SurveyResultsAnalysis.helpers import load_from_official_statistics, load_official_inflation, \
    load_usdrub, saveMatricesToExcel, getFeaturesDescriptions

rootFolder = Path('../data/SurveyResults/')

modellingResults = [
        ('mlcluster_qwen38_async_all_prevexp_-6d', 'QWEN 3.8 (все данные + IE - markers, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_time', 'QWEN 3.6 (все данные, в день Инфом)'),
        #('mlcluster_qwen36_async_all_time_week_before', 'QWEN 3.6 (все данные, -7d от Инфом)'),
        #('mlcluster_qwen36_async_all_two_weekbefore', 'QWEN 3.6 (все данные, -2w от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time_week_before', 'QWEN 3.6 (без usdrub, -7d от Инфом)'),
        #('mlcluster_qwen36_async_nousdrub_time', 'QWEN 3.6 (без usdrub, в день Инфом)'),
        ('mlcluster_qwen36_async_norlms_weekbefore', 'QWEN 3.6 (без RLMS, -7d от Инфом)'),
        ('mlcluster_qwen36_async_only_rlms_-1week', 'QWEN 3.6 (только RLMS, -7d от Инфом)'),
        ('mlcluster_qwen38_async_no_rlms_prevexp_-6d', 'QWEN 3.8 (без RLMS + IE - markers, -7d от Инфом)'),
        ('mlcluster_qwen38_async_no_goods_no_previous_ie_prevexp_-6d', 'QWEN 3.8 (RLMS pass - markers - IE - , -7d от Инфом)'),
        ('mlcluster_qwen38_async_no_rlms_-6d', 'QWEN 3.8 (без RLMS без IE без маркеров + общ инфо, -7d от Инфом'),
        ('mlcluster_qwen38_async_norlms_noIE_keyrate_-6d', 'QWEN 3.8 (без RLMS без IE + ключ, -7d от Инфом)'),
        ('mlcluster_qwen36_async_rlms_pass_noIE_keyrate_-6d', 'QWEN 3.8 (RLMS pass -IE + ключ, -7d от Инфом)'),
        ('mlcluster_qwen36_async_rlms_pass_noIE_keyrate_news_-6d', 'QWEN 3.8 (news + RLMS pass -IE + ключ, -7d от Инфом)'),
        ('mlcluster_qwen36_async_no_rlms_pass_noIE_keyrate_news_-6d', 'QWEN 3.8 (news - RLMS - IE + ключ, 7d от Инфом)'),
        ('mlcluster_qwen36_async_rlms_expenses_noIE_keyrate_news_-6d', 'QWEN 3.8 (news + RLMS e - IE + ключ, 7d от Инфом)'),
        ('mlcluster_qwen36_async_norlms_pass_noIE_nokeyrate_-6d', 'QWEN 3.8 (news + RLMS e - IE - ключ, 7d от Инфом)'),
        ('mlcluster_qwen38_async_norlms_pass_noIE_nokeyrate_nonews_-6d', 'QWEN 3.8 (RLMS e -news -IE -ключ, 7d от Инфом)'),
        ('mlcluster_qwen38_async_norlms_noIE_nokeyrate_-6d', 'QWEN 3.8 (-RLMS +news -IE -ключ, 7d от Инфом)'),
        ('mlcluster_qwen38_async_rlmse_news_nomarkers_-6d', 'QWEN 3.8 (+RLMS e +news -markers, 7d)'),
        ('mlcluster_qwen38_async_news_rlmse_reginf_-6d', 'QWEN 3.8 (+RLMS e +news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_news_rlmsfull_reginf_-6d', 'QWEN 3.8 (+RLMS full  +news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_no_news_rlmsfull_reginf_-6d', 'QWEN 3.8 (+RLMS full  -news +reg inf, 7d)')
]

featuresDescriptionPath = Path('../data/LLMSurveys_Configurations.xlsx')
OOSStartPoints = 129

nStepsAhead = [1, 2, 3, 4, 5, 6]
useDelta = [False]
useOOS = [True, False]
useExpandingOOS = [True]

includeDatesFilter = []
excludeDatesFilter = [('До 01.01.2022', '2022-01-01', '2027-02-01'), ('Без начала СВО 23.02.22-01.06.22', '2022-02-23', '2022-06-01'), ('Весь период', '2030-01-01', '2030-01-02'), ('После 01.01.2022', '2000-01-01', '2022-01-01')]
#excludeDatesFilter = [('После 01.01.2020', '2000-01-01', '2020-01-01')]

surveyResults = loadSurveyResults(rootFolder, modellingResults)

keyRateProvider = KeyRateProvider(visualizationConfiguration.keyRatePath)
directEstimations = load_from_official_statistics(visualizationConfiguration.directInflationEstimationsPath, 1)
officialInflation = load_official_inflation(visualizationConfiguration.officialInflationPath)
usdrubRate = load_usdrub(visualizationConfiguration.usdrubPath)

headers = ['Relative RMSE Gain AR(1) + LLM vs AR(1)', 'Clark-West test AR(1) + LLM vs AR(1)', 'Share of points LLM is better', 'Median LOO', 'MIN LOO', 'Share of best point in total gain', 'Adj. R² gain']
green_max_flags = [True, False, True, True, True, False, True]
tStart = time.time()

row_names = [x[1] for x in modellingResults]
col_names = [f'{f'{x - 1} мес + ' if x > 1 else ''}1 нед' for x in nStepsAhead]

featuresMatrix = getFeaturesDescriptions(featuresDescriptionPath, row_names)

for i_excludeDatesFilter in range(len(excludeDatesFilter)):
    print(f'[{time.time() - tStart:.2f}s] Датасет: {excludeDatesFilter[i_excludeDatesFilter]}')
    for i_useDelta in range(len(useDelta)):
        for i_useOOS in range(len(useOOS)):
            for i_useExpandingOOS in range(len(useExpandingOOS)):

                isDelta = useDelta[i_useDelta]
                isOOS = useOOS[i_useOOS]
                isExpandingOOS = useExpandingOOS[i_useExpandingOOS]
                excludeDate = excludeDatesFilter[i_excludeDatesFilter]

                baseVariables = 'X5' if isDelta else 'X1'
                datesToExclude = (np.datetime64(excludeDate[1]), np.datetime64(excludeDate[2]))
                surveyRegressionService = SurveyRegressionService(directEstimations, officialInflation, usdrubRate,
                                                                  keyRateProvider, datesToExclude)

                relativeRMSEGain = np.zeros((len(modellingResults), len(nStepsAhead)))
                pValueCWTest = np.zeros((len(modellingResults), len(nStepsAhead)))
                shareOfLLMBetter = np.zeros((len(modellingResults), len(nStepsAhead)))
                loom = np.zeros((len(modellingResults), len(nStepsAhead)))
                minloo = np.zeros((len(modellingResults), len(nStepsAhead)))
                shareOfBestPoint = np.zeros((len(modellingResults), len(nStepsAhead)))
                adjRSquared = np.zeros((len(modellingResults), len(nStepsAhead)))

                matrices = [relativeRMSEGain, pValueCWTest, shareOfLLMBetter, loom, minloo, shareOfBestPoint, adjRSquared]

                for i in range(len(modellingResults)):
                    print(f'[{time.time() - tStart:.2f}s] Model: {modellingResults[i][1]}')
                    modelKey = modellingResults[i][1]

                    survey = surveyResults[modelKey]

                    targetModelVariables = (['X3', baseVariables], 'Y')
                    baseModelVariables = ([baseVariables], 'Y')

                    for j in range(len(nStepsAhead)):
                        curNMonth=nStepsAhead[j]

                        ty, tr, tm, tdates = surveyRegressionService.fitWithConfig(survey, targetModelVariables, isDelta, isOOS, isExpandingOOS, start_n=OOSStartPoints, nMonth=curNMonth)
                        by, br, bm, bdates = surveyRegressionService.fitWithConfig(survey, baseModelVariables, isDelta, isOOS, isExpandingOOS, start_n=OOSStartPoints, nMonth=curNMonth)

                        e_llm = ty - tr
                        e_base = by - br

                        fr = ForecastRobustness(e_llm, e_base)
                        #fr.print_robustness_report(block_size=4, n_boot=10_000, hac_lags=3)
                        loo_results, loo = fr.leave_one_out_gain()
                        cw = fr.clark_west_test()

                        sse = loo['full_gain_percent']
                        relativeRMSEGainValue = 1 - math.sqrt(1 - sse/100)

                        relativeRMSEGain[i, j] = relativeRMSEGainValue
                        minloo[i, j] = loo['loo_min_percent'] / 100
                        loom[i, j] = loo['loo_median']
                        shareOfLLMBetter[i, j] = loo['share_positive']
                        shareOfBestPoint[i, j] = (loo["full_gain"] - loo["loo_min"]) / loo["full_gain"]
                        pValueCWTest[i, j] = cw["p_value_one_sided"]

                        if not isOOS:
                            adjRSquared[i, j] = tm.rsquared_adj - bm.rsquared_adj

                filePrefix = f'{excludeDate[0]}_{'delta' if isDelta else 'level'}_{'oos' if isOOS else 'in sample'}_{'expanding' if isExpandingOOS else 'fixed split'}_start points={OOSStartPoints}'
                saveMatricesToExcel(matrices, headers, filePrefix, row_names, col_names, green_max_flags, featuresMatrix)