import asyncio
from pathlib import Path

from Configuration import configuration
from Configuration.configuration import mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSHAPPromptBuilders
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.surveyHelpers import createAsyncSurveyRunner, copyPromptTemplatesToFolder, \
    getDatesFromStrings, createSHAPSurveyRunner

experimentUniqueName='mlcluster_qwen36_async_shap'
profilesFolder = Path('./data/Target profiles')
profilesCount = 5
resultsFolder = Path('data/Shap Results/')/experimentUniqueName
copyPromptTemplatesToFolder(Path('SurveyLogic/PromptBuilders/Prompts/'), resultsFolder/'Prompts')

surveyDates = getDatesFromStrings(['24.02.2022'])

logger = SimpleLogger()

surveyer = AsyncSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger, baseUrl=configuration.mlclusterUrl)
#surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)
systemPromptBuilder, promptBuilders, names = createSHAPPromptBuilders()

for surveyDate in surveyDates:
    runner = createSHAPSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilders, names, surveySerializer, surveyer, profilesCount,
                                     logger)
    surveyResults = runner.RunSurvey(surveyDate)
    surveySerializer.saveSurvey(surveyResults, surveyDate)
