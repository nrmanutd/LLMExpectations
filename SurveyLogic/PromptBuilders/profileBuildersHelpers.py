from Configuration import configuration
from SHAPAnalysis.shapHelpers import getBitArray
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.NewsPromptBuilder import NewsPromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.CommonProfilePromptBuilder import \
    CommonProfilePromptBuilder
from SurveyLogic.PromptBuilders.PromptBuilderFactory import PromptBuilderFactory
from SurveyLogic.PromptBuilders.Prompts import prompts
from SurveyLogic.PromptBuilders.StatisticsProviders.AverageExpensesProvider import AverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.ConvertingAverageExpensesProvider import \
    ConvertingAverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider
from SurveyLogic.PromptBuilders.SystemPromptBuilder import SystemPromptBuilder
from SurveyLogic.PromptBuilders.TaskPromptBuilder import TaskPromptBuilder
from experimentsConfiguration import ExperimentsConfiguration


def createSimplePromptBuilder() -> (BasePromptBuilder, BasePromptBuilder):
    builders = []

    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt))
    builders.append(TaskPromptBuilder(prompts.taskPrompt))

    headers = ['Основные параметры опроса и респондента', 'Задача']

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)

def createNewsPromptBuilder() -> (BasePromptBuilder, BasePromptBuilder):
    builders = []

    mrotProvider = MROTProvider(configuration.mrotStatisticsPath)
    averageBuyingsProvider = AverageExpensesProvider(configuration.averageBuyingsDataPath)
    averageBuyingsProvider = ConvertingAverageExpensesProvider(averageBuyingsProvider,
                                                               configuration.rlmsToInflationRegionsPath)

    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt, mrotProvider, averageBuyingsProvider))
    builders.append(NewsPromptBuilder())
    builders.append(TaskPromptBuilder(prompts.taskPrompt))

    headers = ['Основные параметры опроса и респондента', 'Новости', 'Задача']

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)

def createSHAPPromptBuilders():
    factory = PromptBuilderFactory()

    systemPromptBuilder = SystemPromptBuilder(prompts.systemPrompt)
    builders = []

    totalBits = 7

    for i in range(2**totalBits):
        arr = getBitArray(i, totalBits)
        cfg = ExperimentsConfiguration(
            useIndividualRLMSData=arr[0],
            useFamilyInformation=arr[1],
            useFamilyExpenses=arr[2],
            useStateExpenses=arr[3],
            useEconomy=arr[4],
            useRegionalInflation=arr[5],
            useStateInflation=arr[6]
            )

        pp = factory.createCustomPromptBuilder(cfg)
        builders.append(pp[1])

    names = ['RLMSIndividual', 'RLMSHH', 'RLMSHHRegionalExpenses', 'RLMSHHStateExpenses', 'Economy', 'RegionalInflation', 'StateInflation']

    return systemPromptBuilder, builders, names[:totalBits]
