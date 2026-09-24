import time
from pathlib import Path

import numpy as np
from joblib import Parallel, delayed

from Configuration import configuration
from SurveyLogic.PromptBuilders.PromptBuilderFactory import PromptBuilderFactory
from SurveyResultsAnalysis.RegressionAnalysis.Learning.StandardDatasetCreator import StandardDatasetCreator
from SurveyResultsAnalysis.RegressionAnalysis.SurveyRegressionService import SurveyRegressionService
from SurveyResultsAnalysis.RegressionAnalysis.regressionHelpers import loadSurveyResults, getLearner
from SurveyResultsAnalysis.RegressionAnalysis.statisticsHelpers import process_one_j
from SurveyResultsAnalysis.helpers import load_from_official_statistics, saveMatricesToExcel, getFeaturesDescriptions

rootFolder = Path('data/SurveyResults/')

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
        ('mlcluster_qwen38_async_no_news_rlmsfull_reginf_-6d', 'QWEN 3.8 (+RLMS full  -news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_no_news_rlms_e_reginf_-6d', 'QWEN 3.8 (+RLMS e  -news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_anews_rlms_full_reginf_-6d', 'QWEN 3.8 (+RLMS full  +anews +reg inf, 7d)'),
        ('mlcluster_qwen38_async_anews_rlms_e_reginf_-6d', 'QWEN 3.8 (+RLMS e  +anews +reg inf, 7d)'),
        ('mlcluster_qwen38_async_news_only_-6d', 'QWEN 3.8 (news only, 7d)'),
        ('mlcluster_qwen38_async_news_reginf_only_-6d', 'QWEN 3.8 (+news +reg inf, 7d)'),
        ('mlcluster_qwen38_async_reginf_only_-6d', 'QWEN 3.8 (reg inf, 7d)'),
        ('mlcluster_qwen38_async_news_rlms_exp_-6d', 'QWEN 3.8 (+news +rlms e, 7d)'),
        ('mlcluster_qwen38_async_only_rlms_exp_-6d', 'QWEN 3.8 (rlms e, 7d)'),
        ('mlcluster_gemma3_27b_async_news_only_-6d', 'Gemma 3 27b (news only, 7d)'),
        ('mlcluster_gemma3_27b_async_news_rlms_e_-6d', 'Gemma 3 27b (+news +rlms e, 7d)'),
        ('mlcluster_llama33_70b_async_news_only_-6d', 'LLama 70b (news only, 7d)')
]
#modellingResults = [modellingResults[-1]]
featuresDescriptionPath = Path('data/LLMSurveys_Configurations.xlsx')

cutoff_dates = [None, np.datetime64('2025-06-01')]

nStepsAhead = [1, 2, 3, 4, 5, 6, 7, 13]
useDelta = [False]
useOOS = [True]
useExpandingOOS = [True]
useDummy = [True]
variables = ['IE', 'CPI']
learnersNames = ['AR(1)', 'AR(2)', 'AR(3)', 'Ridge', 'XGBoost']
#learnersNames = ['Ridge', 'Elastic Net', 'XGBoost']

includeDatesFilter = []
#excludeDatesFilter = [('До 01.01.2022', '2022-01-01', '2027-02-01'), ('Без начала СВО 23.02.22-01.06.22', '2022-02-23', '2022-06-01'), ('Весь период', '2030-01-01', '2030-01-02'), ('После 01.01.2022', '2000-01-01', '2022-01-01')]
excludeDatesFilter = [('Весь период', '2030-01-01', '2030-01-02')]

surveyResults = loadSurveyResults(rootFolder, modellingResults)
directEstimations = load_from_official_statistics(configuration.inflationExpectations, 1)

inflationProvider = PromptBuilderFactory.createInflationProvider()
usdrubRateProvider = PromptBuilderFactory.createCurrencyProvider()
keyRateProvider = PromptBuilderFactory.createKeyRateProvider()
inflationExpectationsProvider = PromptBuilderFactory.createInflationExpectationsProvider()

green_max_flags = [True, False, False, True, True, True, False, True]
tStart = time.time()

row_names = [x[1] for x in modellingResults]
col_names = [f'{f'{x - 1} мес + ' if x > 1 else ''}1 нед' for x in nStepsAhead]

featuresMatrix = getFeaturesDescriptions(featuresDescriptionPath, row_names)
for i_learner in range(len(learnersNames)):
    for i_cutoff_date in range(len(cutoff_dates)):
        for i_excludeDatesFilter in range(len(excludeDatesFilter)):
            print(f'[{time.time() - tStart:.2f}s] Датасет: {excludeDatesFilter[i_excludeDatesFilter]}')
            for var in variables:
                for i_useDelta in range(len(useDelta)):
                    for i_useOOS in range(len(useOOS)):
                        for i_useExpandingOOS in range(len(useExpandingOOS)):
                            for i_useDummy in range(len(useDummy)):
                                isDelta = useDelta[i_useDelta]
                                isOOS = useOOS[i_useOOS]
                                isExpandingOOS = useExpandingOOS[i_useExpandingOOS]
                                excludeDate = excludeDatesFilter[i_excludeDatesFilter]
                                isDummy = useDummy[i_useDummy]
                                learnerName = learnersNames[i_learner]
                                cutoff_date = cutoff_dates[i_cutoff_date]

                                variablesProvider, learner = getLearner(isDelta, isDummy, featuresMatrix, learnerName)

                                datesToExclude = (np.datetime64(excludeDate[1]), np.datetime64(excludeDate[2]))

                                headers = [f'Relative RMSE Gain {learnerName} + LLM vs {learnerName}', f'LLM + {learnerName} RMSE',
                                           f'Clark-West test {learnerName} + LLM vs {learnerName}', 'Share of points LLM is better',
                                           'Median LOO', 'MIN LOO', 'Share of best point in total gain', 'Adj. R² gain']

                                relativeRMSEGain = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                llmRMSE = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                pValueCWTest = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                shareOfLLMBetter = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                loom = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                minloo = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                shareOfBestPoint = np.full((len(modellingResults), len(nStepsAhead)), np.nan)
                                adjRSquared = np.full((len(modellingResults), len(nStepsAhead)), np.nan)

                                matrices = [relativeRMSEGain, llmRMSE, pValueCWTest, shareOfLLMBetter, loom, minloo, shareOfBestPoint, adjRSquared]

                                dataSetCreator = StandardDatasetCreator(directEstimations, inflationProvider,
                                                                        usdrubRateProvider,
                                                                        keyRateProvider, inflationExpectationsProvider, var,
                                                                        isDelta, isDummy,
                                                                        datesToExclude)

                                surveyRegressionService = SurveyRegressionService(dataSetCreator, learner)
                                #surveyRegressionService = CachingSurveyRegressionService(surveyRegressionService)

                                for i in range(len(modellingResults)):
                                    print(f'[{time.time() - tStart:.2f}s] Model #{i + 1} of {len(modellingResults)}: {modellingResults[i][1]}')
                                    modelKey = modellingResults[i][1]

                                    survey = surveyResults[modelKey]
                                    baseVariables = variablesProvider.getBaseVariables(modelKey)

                                    targetModelVariables = (['X3'] + baseVariables, 'Y')
                                    baseModelVariables = (baseVariables, 'Y')

                                    if isDummy:
                                        targetModelVariables[0].append('X7')
                                        baseModelVariables[0].append('X7')

                                    results = Parallel(n_jobs=-1, backend="loky", verbose=10)(
                                        delayed(process_one_j)(
                                            j, survey, surveyRegressionService, targetModelVariables, baseModelVariables,
                                            isOOS, isExpandingOOS, cutoff_date, nStepsAhead, tStart
                                        )
                                        for j in range(len(nStepsAhead))
                                    )

                                    for j, res in enumerate(results):
                                        if res is None:
                                            continue
                                        relativeRMSEGain[i, j] = res['relativeRMSEGain']
                                        llmRMSE[i, j] = res['llmRMSE']
                                        minloo[i, j] = res['minloo']
                                        loom[i, j] = res['loom']
                                        shareOfLLMBetter[i, j] = res['shareOfLLMBetter']
                                        shareOfBestPoint[i, j] = res['shareOfBestPoint']
                                        pValueCWTest[i, j] = res['pValueCWTest']
                                        if not isOOS:
                                            adjRSquared[i, j] = res['adjRSquared']

                                filePrefix = f'{var}_{excludeDate[0]}_{'delta' if isDelta else 'level'}_{'oos' if isOOS else 'in sample'}_{'expanding' if isExpandingOOS else 'fixed split'}_cutoff_date={cutoff_date}_{'dummy' if isDummy else 'no_dummy'}_{learnerName}_({len(modellingResults)})'
                                saveMatricesToExcel(matrices, headers, filePrefix, row_names, col_names, green_max_flags, featuresMatrix)