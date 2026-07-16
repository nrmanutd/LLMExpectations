from datetime import date

from Configuration.configuration import bothub_key
from SurveyLogic.PromptBuilders.Profiles.FixedProfilesProvider import FixedProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createSimplePromptBuilder
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.BothubSurveyer import BothubSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer

profilesLoader = ProfileDataLoader()
profiles = profilesLoader.loadProfiles('.\\data\\target_rlms2024_os_based_profiles')
surveyDate = date(2025, 7, 1)

systemPromptBuilder, promptBuilder = createSimplePromptBuilder()
#surveyer = BothubSurveyer(modelToUse='deepseek-v4-pro', key=bothub_key)
surveyer = StubSurveyer()
profilesProvider = FixedProfilesProvider(profiles)

surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
surveySerializer = SurveySerializer('rlms2024', 'data\\target_rlms2024_os_based_profiles_results')
runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider)

surveyResults = runner.RunSurvey(surveyDate)

surveySerializer.saveSurvey(surveyResults, surveyDate)
