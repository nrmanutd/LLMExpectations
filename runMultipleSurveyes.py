from datetime import date
from pathlib import Path
import pandas as pd

from Configuration.configuration import bothub_key, mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder, createCustomPromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.AdditionalInformationSurveyExecutor import AdditionalInformationSurveyExecutor
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.BothubSurveyer import BothubSurveyer
from SurveyLogic.Surveyers.MLClusterSurveyer import MLClusterSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createSurveyRunner

logger = SimpleLogger()
profilesFolder = Path('./data/Target profiles')
resultsFolder = Path('data/SurveyResults/mlcluster_qwen36_no_inflation_no_politics_no_date_2016_2026_QS')
surveyDates = pd.date_range(start='2016-04-01', end='2026-04-01', freq='QS', inclusive='both').tolist()

#systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
systemPromptBuilder, promptBuilder = createCustomPromptBuilder(useEconomy=False, usePolitics=False, useStateInflation=True, useRegionalInflation=True)

#surveyer = BothubSurveyer(modelToUse='deepseek-v4-pro', key=bothub_key, logger=logger)
#surveyer = MLClusterSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger)
surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)
runner = createSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilder, surveySerializer, surveyer, logger)

for surveyDate in surveyDates:
    surveyResults = runner.RunSurvey(surveyDate)
    surveySerializer.saveSurvey(surveyResults, surveyDate)
