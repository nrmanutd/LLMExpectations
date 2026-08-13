import asyncio
from pathlib import Path

from Configuration import configuration
from Configuration.configuration import mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSHAPPromptBuilders
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createAsyncSurveyRunner, copyPromptTemplatesToFolder, \
    getDatesFromStrings, createSHAPSurveyRunner

experimentUniqueName='mlcluster_qwen36_async_shap'
profilesFolder = Path('./data/Target profiles')
profilesCount = 100
resultsFolder = Path('data/Shap Results/')/experimentUniqueName
copyPromptTemplatesToFolder(Path('SurveyLogic/PromptBuilders/Prompts/'), resultsFolder/'Prompts')

surveyDates = getDatesFromStrings(['09.07.2026', '08.05.2018', '09.12.2014', '05.03.2020'])

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
