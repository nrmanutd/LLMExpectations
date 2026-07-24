from datetime import date
from pathlib import Path
import pandas as pd

from Configuration.configuration import bothub_key, mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder, createCustomPromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.BothubSurveyer import BothubSurveyer
from SurveyLogic.Surveyers.MLClusterSurveyer import MLClusterSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer

logger = SimpleLogger()
profilesFolder = Path('.\\data\\Target profiles')
surveyDates = dates = pd.date_range(start='2016-01-01', end='2026-01-01', freq='QS', inclusive='both').tolist()

#systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
systemPromptBuilder, promptBuilder = createCustomPromptBuilder(useInflation=False, usePolitics=False)
#surveyer = BothubSurveyer(modelToUse='deepseek-v4-pro', key=bothub_key, logger=logger)
surveyer = MLClusterSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger)
#surveyer = StubSurveyer()


profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
surveySerializer = SurveySerializer('mlcluster_qwen36_custom_inflation_politics_2020_2020_QS', 'data\\SurveyResults')
runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider, logger)

for surveyDate in surveyDates:
    surveyResults = runner.RunSurvey(surveyDate)
    surveySerializer.saveSurvey(surveyResults, surveyDate)
