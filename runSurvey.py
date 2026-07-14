from datetime import date

from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer

profilesLoader = ProfileDataLoader()
profiles = profilesLoader.loadProfiles('.\\data')
surveyDate = date(2025, 7, 1)

surveyExecutor = StandardSurveyExecutor()
surveySerializer = SurveySerializer('rlms2025', 'surveyResults')
runner = StandardSurveyRunner(surveySerializer, surveyExecutor)

surveyResults = runner.RunSurvey(surveyDate, profiles)

surveySerializer.saveSurvey(surveyResults, surveyDate)
