import asyncio
from datetime import date
from pathlib import Path
import pandas as pd

from Configuration.configuration import bothub_key, mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.AsyncSurveyRunner import AsyncSurveyRunner
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder, createCustomPromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.AdditionalInformationSurveyExecutor import AdditionalInformationSurveyExecutor
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.BothubSurveyer import BothubSurveyer
from SurveyLogic.Surveyers.MLClusterSurveyer import MLClusterSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createSurveyRunner, createAsyncSurveyRunner

logger = SimpleLogger()
profilesFolder = Path('./data/Target profiles')
resultsFolder = Path('data/SurveyResults/mlcluster_qwen36_hh_detailed_with_personal_prices_2016_2026_QS')
surveyDates = pd.date_range(start='2016-01-01', end='2026-04-01', freq='QS', inclusive='both').tolist()

#systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
systemPromptBuilder, promptBuilder = createCustomPromptBuilder(useEconomy=False, usePolitics=False, useStateInflation=False, useRegionalInflation=False, useFamilyInformation=True, useFamilyExpenses=True)

#surveyer = BothubSurveyer(modelToUse='deepseek-v4-pro', key=bothub_key, logger=logger)
#surveyer = MLClusterSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger)
surveyer = AsyncSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger)
#surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)

for surveyDate in surveyDates:
    runner = createAsyncSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilder, surveySerializer, surveyer,
                                     logger)
    surveyResults = asyncio.run(runner.RunSurvey(surveyDate))
    surveySerializer.saveSurvey(surveyResults, surveyDate)
