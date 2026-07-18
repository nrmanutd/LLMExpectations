from datetime import date
from pathlib import Path
import pandas as pd

from Configuration.configuration import bothub_key
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder, createCustomPromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.BothubSurveyer import BothubSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer

profilesFolder = Path('.\\data\\Target profiles')

surveyDates = dates = pd.date_range(start='2020-01-01', end='2020-04-01', freq='QS', inclusive='both').tolist()

systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
#systemPromptBuilder, promptBuilder = createCustomPromptBuilder(useInflation=True, usePolitics=True)
surveyer = BothubSurveyer(modelToUse='deepseek-v4-pro', key=bothub_key)
#surveyer = StubSurveyer()
profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
surveySerializer = SurveySerializer('simple_2020_2020_QS', 'data\\SurveyResults')
runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider)

for surveyDate in surveyDates:
    surveyResults = runner.RunSurvey(surveyDate)
    surveySerializer.saveSurvey(surveyResults, surveyDate)
