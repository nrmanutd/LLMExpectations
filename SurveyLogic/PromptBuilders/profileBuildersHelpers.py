from Configuration import configuration
from SHAPAnalysis.shapHelpers import getBitArray
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
from SurveyLogic.PromptBuilders.ConstantPromptBuilder import ConstantPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.NewsPromptBuilder import NewsPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.RegionalInflationContextPromptBuilder import \
    RegionalInflationContextPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.StateEconomyContextPromptBuilder import \
    StateEconomyContextPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.StateInflationContextPromptBuilder import \
    StateInflationContextPromptBuilder
from SurveyLogic.PromptBuilders.MonthlyFromFilePromptBuilder import MonthlyFromFilePromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.CommonProfilePromptBuilder import \
    CommonProfilePromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.ExpensesProfilePromptBuilder import \
    ExpensesProfilePromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.HouseholdProfilePromptBuilder import \
    HouseholdProfilePromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.StateExpensesProfilePromptBuilder import \
    StateExpensesProfilePromptBuilder
from SurveyLogic.PromptBuilders.PromptBuilderFactory import PromptBuilderFactory
from SurveyLogic.PromptBuilders.StatisticsProviders.AverageExpensesProvider import AverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.ConvertingAverageExpensesProvider import \
    ConvertingAverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.ConvertingInflationProvider import ConvertingInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.DateRoundingSingleMonthInflationProvider import \
    DateRoundingSingleMonthInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.EMISSWebSingleMonthInflationProvider import \
    EMISSWebSingleMonthInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.InflationProvider import InflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.MultipleEMISSFilesInflationProvider import \
    MultipleEMISSFilesInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.MultipleWeeklyInflationProvider import \
    MultipleWeeklyInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.RosstatWeeklyInflationProvider import \
    RosstatWeeklyInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.USDRUBRateProvider import USDRUBRateProvider
from SurveyLogic.PromptBuilders.SystemPromptBuilder import SystemPromptBuilder
from SurveyLogic.PromptBuilders.Prompts import prompts
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

    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt))
    builders.append(NewsPromptBuilder())
    builders.append(TaskPromptBuilder(prompts.taskPrompt))

    headers = ['Основные параметры опроса и респондента', 'Новости', 'Задача']

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)

def createSHAPPromptBuilders():
    factory = PromptBuilderFactory()

    systemPromptBuilder = SystemPromptBuilder(prompts.systemPrompt)
    builders = []

    for i in range(128):
        print(i)
        arr = getBitArray(i, 7)
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

    return systemPromptBuilder, builders, names
