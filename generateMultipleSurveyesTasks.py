from pathlib import Path

import pandas as pd

from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.BatchesSerializer import BatchesSerializer
from SurveyLogic.Surveyers.BatchCollectingSurveyer import BatchCollectingSurveyer

logger = SimpleLogger()
profilesFolder = Path('.\\data\\Target profiles')
surveyDates = dates = pd.date_range(start='2020-01-01', end='2020-04-01', freq='QS', inclusive='both').tolist()

systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
surveyer = BatchCollectingSurveyer('deepseek-v4-pro')
surveySerializer = BatchesSerializer('custom_inflation_politics_2020_2020_QS', 'data\\SurveyTasksToExecute')

profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider, logger)

for surveyDate in surveyDates:
    surveyResults = runner.RunSurvey(surveyDate)
    surveySerializer.saveSurvey(surveyResults, surveyDate)
