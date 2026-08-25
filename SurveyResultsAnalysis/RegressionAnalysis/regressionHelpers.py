from pathlib import Path

from SurveyResultsAnalysis.helpers import load_pdtable, aggregate_survey


def loadSurveyResults(rootFolder: Path, surveyResults):
    models = {}
    for folder, name in surveyResults:
        f = rootFolder / folder
        s = load_pdtable(f)
        s = aggregate_survey(s)

        models[name] = s

    return models