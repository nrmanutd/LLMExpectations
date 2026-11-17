from Configuration import configuration
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
from SurveyLogic.PromptBuilders.ConstantPromptBuilder import ConstantPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.KeyRatePromptBuilder import \
    KeyRatePromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.MarkerGoodsInflationPromptBuilder import \
    MarkerGoodsInflationPromptBuilder
from SurveyLogic.PromptBuilders.ContextPromptBuilders.StatePromptBuilders.PrevoiusInflationExpectationsPromptBuilder import \
    PrevoiusInflationExpectationsPromptBuilder
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
from SurveyLogic.PromptBuilders.Prompts import prompts
from SurveyLogic.PromptBuilders.StatisticsProviders.AverageExpensesProvider import AverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.ConvertingAverageExpensesProvider import \
    ConvertingAverageExpensesProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationExpectationsProvider import InflationExpectationsProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseInflationProvider import \
    BaseInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.BaseSingleMonthInflationProvider import \
    BaseSingleMonthInflationProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.InflationProviderLogic.ConvertingInflationProvider import \
    ConvertingInflationProvider
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
from SurveyLogic.PromptBuilders.StatisticsProviders.KeyRateProvider import KeyRateProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.MROTProvider import MROTProvider
from SurveyLogic.PromptBuilders.StatisticsProviders.USDRUBRateProvider import USDRUBRateProvider
from SurveyLogic.PromptBuilders.SystemPromptBuilder import SystemPromptBuilder
from SurveyLogic.PromptBuilders.TaskPromptBuilder import TaskPromptBuilder

from experimentsConfiguration import ExperimentsConfiguration


class PromptBuilderFactory:
    def __init__(self):
        self.noInformationPromptBuilder = ConstantPromptBuilder('Нет информации')
        mrotProvider = MROTProvider(configuration.mrotStatisticsPath)
        averageBuyingsProvider = AverageExpensesProvider(configuration.averageBuyingsDataPath)
        averageBuyingsProvider = ConvertingAverageExpensesProvider(averageBuyingsProvider,
                                                                   configuration.rlmsToInflationRegionsPath)

        self.commonProfilePromptBuilder = CommonProfilePromptBuilder(prompts.respondentPrompt, mrotProvider, averageBuyingsProvider)

        self.inflationProvider = self.createInflationProvider()

        self.householdInformationBuilder = HouseholdProfilePromptBuilder(prompts.househouldCommonPrompt,
                                                                        averageBuyingsProvider)
        self.expensesProfilePromptBuilder = ExpensesProfilePromptBuilder(prompts.expensesPrompt, self.inflationProvider,
                                                                        [configuration.regularGoods,
                                                                         configuration.durableGoods,
                                                                         configuration.services])
        paths = [configuration.weeklyRegularGoods, configuration.weeklyDurableGoods, configuration.weeklyServices]
        self.stateExpensesPromptBuilder = StateExpensesProfilePromptBuilder(prompts.stateWeeklyExpensesPrompt,
                                                                           self.inflationProvider, paths)
        self.stateInflationProvider = StateInflationContextPromptBuilder(prompts.stateInflationPrompt, self.inflationProvider)
        self.regionInflationProvider = RegionalInflationContextPromptBuilder(prompts.regionInflationPrompt,
                                                                            self.inflationProvider)
        self.currencyProvider = self.createCurrencyProvider()

        self.stateEconomyContextPromptBuilder = StateEconomyContextPromptBuilder(prompts.stateEconomyPrompt, self.currencyProvider)

        self.politicsProvider = MonthlyFromFilePromptBuilder(prompts.politicsPath)
        self.newsProvider = MonthlyFromFilePromptBuilder(prompts.newsPath)
        self.anonymizedNewsProvider = MonthlyFromFilePromptBuilder(prompts.anonymizedNewsPath)

        self.taskPromptBuilder = TaskPromptBuilder(prompts.taskPrompt)

        self.markerGoodsInflationProvider = MarkerGoodsInflationPromptBuilder(self.inflationProvider, configuration.regularMarkerGoods, configuration.durableMarkerGoods, configuration.servicesMarker)
        self.inflationExpectationsProvider = self.createInflationExpectationsProvider()

        self.previousInflationExpectationsPromptBuilder = PrevoiusInflationExpectationsPromptBuilder(self.inflationExpectationsProvider)

        self.keyRateProvider = self.createKeyRateProvider()
        self.keyRatePromptBuilder = KeyRatePromptBuilder(self.keyRateProvider)

    @staticmethod
    def createInflationExpectationsProvider() -> InflationExpectationsProvider:
        return InflationExpectationsProvider(configuration.inflationExpectations)

    @staticmethod
    def createKeyRateProvider() -> KeyRateProvider:
        return KeyRateProvider(configuration.keyRateFile)

    @staticmethod
    def createCurrencyProvider() -> USDRUBRateProvider:
        return USDRUBRateProvider(configuration.usdrubDataPath)

    @staticmethod
    def createInflationProvider() -> BaseInflationProvider:
        multipleWeeklyProvider = MultipleWeeklyInflationProvider(configuration.weeklyInflationDataPath,
                                                                 list(range(2022, 2027)))
        weeklyInflationProvider = RosstatWeeklyInflationProvider(multipleWeeklyProvider)

        singleMonthInflationProvider = PromptBuilderFactory._createSingleMonthInflationProvider()
        singleMonthInflationProvider = DateRoundingSingleMonthInflationProvider(singleMonthInflationProvider)

        inflationProvider = InflationProvider(singleMonthInflationProvider, weeklyInflationProvider)
        inflationProvider = ConvertingInflationProvider(inflationProvider, configuration.rlmsToInflationRegionsPath)
        return inflationProvider

    @staticmethod
    def _createSingleMonthInflationProvider() -> BaseSingleMonthInflationProvider:
        files = [configuration.inflation20092014DataPath, configuration.inflation20152020DataPath,
                 configuration.inflation20212026DataPath]
        yearsSets = [configuration.years20092014, configuration.years20152020, configuration.years20212026]
        providers = [EMISSWebSingleMonthInflationProvider(x) for x in files]

        singleMonthInflationProvider = MultipleEMISSFilesInflationProvider(providers, yearsSets)
        return singleMonthInflationProvider

    def createCustomPromptBuilder(self, cfg: ExperimentsConfiguration):
        builders = []
        headers = []

        if cfg.useIndividualRLMSData:
            builders.append(self.commonProfilePromptBuilder)
            headers.append('Основные параметры опроса и респондента')

        if cfg.useFamilyInformation:
            builders.append(self.householdInformationBuilder)
            headers.append('Детальная информация о домохозяйстве, членом которого является индивид')

        if cfg.useFamilyExpenses:
            builders.append(self.expensesProfilePromptBuilder)
            headers.append(
                'Детальная информация об инфляции на уровне региона на товары в топ-расходах семьи индивида (регулярные траты, товары длительного использования, услуги)')

        if cfg.useStateExpenses:
            builders.append(self.stateExpensesPromptBuilder)
            headers.append(
                'Детальная наиболее свежая информация об инфляции на уровне Российской Федерации в целом на товары, покупаемые домохозяйством')

        if cfg.useMarkerGoods:
            builders.append(self.markerGoodsInflationProvider)
            headers.append('Инфляция по товарам-маркерам в РФ и регионе проживания')

        if cfg.useRegionalInflation:
            builders.append(self.regionInflationProvider)
            headers.append('Официальная государственная статистика по инфляции в регионе проживания в целом')

        if cfg.useInflation:
            builders.append(self.stateInflationProvider)
            headers.append('Официальная государственная статистика по инфляции по РФ в целом')

        if cfg.useEconomy:
            builders.append(self.stateEconomyContextPromptBuilder)
            headers.append('Основная информация об экономических показателях РФ в целом в мире')

        if cfg.usePreviousInflationExpectations:
            builders.append(self.previousInflationExpectationsPromptBuilder)
            headers.append('Предыдущие агрегированные инфляционные ожидания')

        if cfg.useNews:
            builders.append(self.newsProvider)
            headers.append('Общий контекст (новости, события в РФ и в мире)')

        if cfg.useANews:
            builders.append(self.anonymizedNewsProvider)
            headers.append('Общий контекст (без указания конкретных новостей и событий)')

        if cfg.usePolitics:
            builders.append(self.politicsProvider)
            headers.append('Основная политико-экономическая информация по РФ в целом')

        if cfg.useKeyRateIncrements:
            builders.append(self.keyRatePromptBuilder)
            headers.append('Общий макроэкономический фон: последние изменения ключевой ставки ЦБ')

        builders.append(self.taskPromptBuilder)
        headers.append('Задача')

        return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)
