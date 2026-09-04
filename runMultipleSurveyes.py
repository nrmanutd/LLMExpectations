import asyncio
from datetime import datetime
from pathlib import Path

from Configuration import configuration
from Configuration.configuration import mlcluster_key
from Logging.SimpleLogger import SimpleLogger
from SurveyExecutionTools.surveyExecutionHelpers import saveExperimentConfiguration
from SurveyLogic.PromptBuilders.PromptBuilderFactory import PromptBuilderFactory
from SurveyLogic.SurveyResultsSerialization.SurveySerializer import SurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.StubSurveyer import StubSurveyer
from SurveyLogic.surveyHelpers import createAsyncSurveyRunner, extractDatesFromFile, copyPromptTemplatesToFolder, \
    getDatesRowWithMonthlyStep, getDatesRowWithWeeklyStep
from experimentsConfiguration import ExperimentsConfiguration

offsetDays = -6
experimentUniqueName=f'mlcluster_qwen36_async_rlms_pass_noIE_keyrate_{offsetDays}d'
profilesFolder = Path('./data/Target profiles')
profilesCount = 100
resultsFolder = Path('data/SurveyResults/')/experimentUniqueName
copyPromptTemplatesToFolder(Path('SurveyLogic/PromptBuilders/Prompts/'), resultsFolder/'Prompts')

surveyDates = extractDatesFromFile(configuration.inflationSurveysDates, offsetDays=offsetDays, start_date=datetime.strptime('2021.12.01', '%Y.%m.%d'), end_date=datetime.strptime('2022.06.01', '%Y.%m.%d'))
#surveyDates = extractDatesFromFile(configuration.inflationSurveysDates, offsetDays=offsetDays)

#surveyDates = getDatesRowWithMonthlyStep('2020.12.01', '2021.01.01')
#surveyDates = getDatesRowWithWeeklyStep('2022.03.12', '2022.05.07')

cfg = ExperimentsConfiguration(
    useIndividualRLMSData=True,
    useFamilyInformation=True,
    useFamilyExpenses=False,
    useStateExpenses=False,
    useMarkerGoods=True,
    useEconomy=True,
    useRegionalInflation=True,
    useInflation=True,
    useKeyRateIncrements=True,
    usePreviousInflationExpectations=False
    )

saveExperimentConfiguration(cfg, resultsFolder)

factory = PromptBuilderFactory()
systemPromptBuilder, promptBuilder = factory.createCustomPromptBuilder(cfg)
logger = SimpleLogger()

#surveyer = AsyncSurveyer(modelToUse='Qwen/Qwen3.8-27B', key=mlcluster_key, logger=logger, baseUrl=configuration.mlclusterUrl)
#surveyer = AsyncSurveyer(modelToUse='qwen3.6-35b-a3b', key=bothub_key, logger=logger, baseUrl=configuration.bothubUrl)
#surveyer = AsyncSurveyer(modelToUse='qwen3.6-27b', key=aitunnel_key, logger=logger, baseUrl=configuration.aitunnelUrl, maxAttempts=100)
surveyer = StubSurveyer()

surveySerializer = SurveySerializer(resultsFolder)

for surveyDate in surveyDates:
    runner = createAsyncSurveyRunner(profilesFolder, systemPromptBuilder, promptBuilder, surveySerializer, surveyer, profilesCount,
                                     logger)
    surveyResults = asyncio.run(runner.RunSurvey(surveyDate))
    surveySerializer.saveSurvey(surveyResults, surveyDate)
