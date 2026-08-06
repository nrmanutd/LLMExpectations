import asyncio
from pathlib import Path

from Configuration import configuration
from Configuration.configuration import mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createCustomPromptBuilder
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createAsyncSurveyRunner, extractDatesFromFile, copyPromptTemplatesToFolder, \
    getDatesRowWithMonthlyStep, getDatesRowWithWeeklyStep

experimentUniqueName='mlcluster_qwen36_async_hh_weekly_2022_02_04'
profilesFolder = Path('./data/Target profiles')
resultsFolder = Path('data/SurveyResults/')/experimentUniqueName
copyPromptTemplatesToFolder(Path('SurveyLogic/PromptBuilders/Prompts/'), resultsFolder/'Prompts')

#surveyDates = extractDatesFromFile(configuration.inflationSurveysDates)
#surveyDates = getDatesRowWithMonthlyStep('2020.12.01', '2021.01.01')
surveyDates = getDatesRowWithWeeklyStep('2022.02.04', '2022.04.01')

systemPromptBuilder, promptBuilder = createCustomPromptBuilder(useEconomy=False, usePolitics=False, useStateInflation=False, useRegionalInflation=False, useFamilyInformation=True, useFamilyExpenses=False, useStateExpenses=True)
logger = SimpleLogger()

surveyer = AsyncSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger, baseUrl=configuration.mlclusterUrl)
#surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)

for surveyDate in surveyDates:
    runner = createAsyncSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilder, surveySerializer, surveyer,
                                     logger)
    surveyResults = asyncio.run(runner.RunSurvey(surveyDate))
    surveySerializer.saveSurvey(surveyResults, surveyDate)
