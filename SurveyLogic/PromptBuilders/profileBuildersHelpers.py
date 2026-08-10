from Configuration import configuration
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
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

def createCustomPromptBuilder(cfg: ExperimentsConfiguration):
    builders = []
    headers = []

    mrotProvider = MROTProvider(configuration.mrotStatisticsPath)
    averageBuyingsProvider = AverageExpensesProvider(configuration.averageBuyingsDataPath)
    averageBuyingsProvider = ConvertingAverageExpensesProvider(averageBuyingsProvider, configuration.rlmsToInflationRegionsPath)

    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt, mrotProvider, averageBuyingsProvider))
    headers.append('Основные параметры опроса и респондента')

    multipleWeeklyProvider = MultipleWeeklyInflationProvider(configuration.weeklyInflationDataPath, list(range(2022, 2027)))
    weeklyInflationProvider = RosstatWeeklyInflationProvider(multipleWeeklyProvider)

    singleMonthInflationProvider = createSingleMonthInflationProvider()
    singleMonthInflationProvider = DateRoundingSingleMonthInflationProvider(singleMonthInflationProvider)

    inflationProvider = InflationProvider(singleMonthInflationProvider, weeklyInflationProvider)
    inflationProvider = ConvertingInflationProvider(inflationProvider, configuration.rlmsToInflationRegionsPath)

    if cfg.useFamilyInformation:
        householdInformationBuilder = HouseholdProfilePromptBuilder(prompts.househouldCommonPrompt, averageBuyingsProvider)
        builders.append(householdInformationBuilder)
        headers.append('Детальная информация о домохозяйстве, членом которого является индивид')

    if cfg.useFamilyExpenses:
        expensesProfilePromptBuilder = ExpensesProfilePromptBuilder(prompts.expensesPrompt, inflationProvider, [configuration.regularGoods, configuration.durableGoods, configuration.services])
        builders.append(expensesProfilePromptBuilder)
        headers.append('Детальная информация об инфляции на уровне региона на товары в топ-расходах семьи индивида (регулярные траты, товары длительного использования, услуги)')

    if cfg.useStateExpenses:
        paths = [configuration.weeklyRegularGoods, configuration.weeklyDurableGoods, configuration.weeklyServices]

        stateExpensesPromptBuilder = StateExpensesProfilePromptBuilder(prompts.stateWeeklyExpensesPrompt, inflationProvider, paths)
        builders.append(stateExpensesPromptBuilder)
        headers.append('Детальная наиболее свежая информация об инфляции на уровне Российской Федерации в целом на товары, покупаемые домохозяйством')

    if cfg.useStateInflation:
        stateInflationProvider = StateInflationContextPromptBuilder(prompts.stateInflationPrompt, inflationProvider)
        builders.append(stateInflationProvider)
        headers.append('Официальная государственная статистика по инфляции')

    if cfg.useRegionalInflation:
        regionInflationProvider = RegionalInflationContextPromptBuilder(prompts.regionInflationPrompt, inflationProvider)
        builders.append(regionInflationProvider)
        headers.append('Официальная государственная статистика по инфляции в регионе проживания индивида')

    if cfg.useEconomy:
        currencyProvider = USDRUBRateProvider(configuration.usdrubDataPath)
        builders.append(StateEconomyContextPromptBuilder(prompts.stateEconomyPrompt, currencyProvider))
        headers.append('Основная информация об экономических показателях РФ в целом в мире')

    if cfg.usePolitics:
        builders.append(MonthlyFromFilePromptBuilder(prompts.politicsPath))
        headers.append('Основная политико-экономическая информация по РФ в целом')

    builders.append(TaskPromptBuilder(prompts.taskPrompt))
    headers.append('Задача')

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)

def createSingleMonthInflationProvider() -> BaseSingleMonthInflationProvider:
    files = [configuration.inflation20092014DataPath, configuration.inflation20152020DataPath,
             configuration.inflation20212026DataPath]
    yearsSets = [configuration.years20092014, configuration.years20152020, configuration.years20212026]
    providers = [EMISSWebSingleMonthInflationProvider(x) for x in files]

    singleMonthInflationProvider = MultipleEMISSFilesInflationProvider(providers, yearsSets)
    return singleMonthInflationProvider
