import asyncio
from datetime import datetime
from pathlib import Path

from Configuration import configuration
from Configuration.configuration import mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyExecutionTools.surveyExecutionHelpers import saveExperimentConfiguration
from SurveyLogic.PromptBuilders.profileBuildersHelpers import createCustomPromptBuilder
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createAsyncSurveyRunner, extractDatesFromFile, copyPromptTemplatesToFolder, \
    getDatesRowWithMonthlyStep, getDatesRowWithWeeklyStep
from experimentsConfiguration import ExperimentsConfiguration

experimentUniqueName='mlcluster_qwen36_async_norlms_weekbefore'
profilesFolder = Path('./data/Target profiles')
profilesCount = 100
resultsFolder = Path('data/SurveyResults/')/experimentUniqueName
copyPromptTemplatesToFolder(Path('SurveyLogic/PromptBuilders/Prompts/'), resultsFolder/'Prompts')

surveyDates = extractDatesFromFile(configuration.inflationSurveysDates, offsetDays=-6)
#surveyDates = getDatesRowWithMonthlyStep('2020.12.01', '2021.01.01')
#surveyDates = getDatesRowWithWeeklyStep('2022.01.12', '2022.05.07')

cfg = ExperimentsConfiguration(
    #useIndividualRLMSData=True,
    #useFamilyInformation=True,
    #useFamilyExpenses=True,
    #useStateExpenses=True,
    useEconomy=True,
    #useRegionalInflation=True,
    useStateInflation=True
    )

saveExperimentConfiguration(cfg, resultsFolder)

systemPromptBuilder, promptBuilder = createCustomPromptBuilder(cfg)
logger = SimpleLogger()

surveyer = AsyncSurveyer(modelToUse='Qwen/Qwen3.6-27B', key=mlcluster_key, logger=logger, baseUrl=configuration.mlclusterUrl)
#surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)

for surveyDate in surveyDates:
    runner = createAsyncSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilder, surveySerializer, surveyer, profilesCount,
                                     logger)
    surveyResults = asyncio.run(runner.RunSurvey(surveyDate))
    surveySerializer.saveSurvey(surveyResults, surveyDate)
