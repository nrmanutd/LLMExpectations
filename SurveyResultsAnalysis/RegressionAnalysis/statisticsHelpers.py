import math
import time
import numpy as np

from SurveyResultsAnalysis.RegressionAnalysis.ForecastRobustness import ForecastRobustness


def process_one_j(j, survey, surveyRegressionService, targetModelVariables, baseModelVariables,
                  isOOS, isExpandingOOS, cutoff_date, nStepsAhead, tStart):
    curNMonth = nStepsAhead[j]
    print(f'[{time.time() - tStart:.2f}s] nStepsAhead = {curNMonth}...')

    ty, tr, tm, tdates = surveyRegressionService.fitWithConfig(
        survey, targetModelVariables, isOOS, isExpandingOOS,
        cutoff_date=cutoff_date, nMonth=curNMonth)
    by, br, bm, bdates = surveyRegressionService.fitWithConfig(
        survey, baseModelVariables, isOOS, isExpandingOOS,
        cutoff_date=cutoff_date, nMonth=curNMonth)

    e_llm = ty - tr
    e_base = by - br
    llm_rmse = np.sqrt(np.mean(e_llm**2))

    if len(e_llm) < 10:
        return None  # сигнал «пропустить»

    fr = ForecastRobustness(e_llm, e_base)
    loo_results, loo = fr.leave_one_out_gain()
    cw = fr.clark_west_test()

    sse = loo['full_gain_percent']
    relativeRMSEGainValue = 1 - math.sqrt(1 - sse/100)

    out = dict(
        relativeRMSEGain=relativeRMSEGainValue,
        llmRMSE=llm_rmse,
        minloo=loo['loo_min_percent'] / 100,
        loom=loo['loo_median'],
        shareOfLLMBetter=loo['share_positive'],
        shareOfBestPoint=(loo["full_gain"] - loo["loo_min"]) / loo["full_gain"],
        pValueCWTest=cw["p_value_one_sided"],
        adjRSquared=(tm.rsquared_adj - bm.rsquared_adj) if not isOOS else None,
    )
    return out