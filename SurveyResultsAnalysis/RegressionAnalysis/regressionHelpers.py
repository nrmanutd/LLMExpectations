import pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from SurveyResultsAnalysis.helpers import load_pdtable, aggregate_survey


def _load_one(rootFolder: Path, folder: str, name: str):
    f = rootFolder / folder
    s = load_pdtable(f)
    s = aggregate_survey(s)
    return name, s

def loadSurveyResults(rootFolder: Path, surveyResults, max_workers: int = 12):
    models = {}
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = [
            ex.submit(_load_one, rootFolder, folder, name)
            for folder, name in surveyResults
        ]
        for fut in as_completed(futures):
            name, s = fut.result()   # дождались — пишем в общий dict
            models[name] = s
    return models

def getSurveyVisualization(predictions, dates):
    result_df = pd.DataFrame({
        'exp_mean': predictions.values
    }, index=dates)

    # Переименовываем индекс в 'date' для ясности (опционально)
    result_df.index.name = 'date'
    return result_df