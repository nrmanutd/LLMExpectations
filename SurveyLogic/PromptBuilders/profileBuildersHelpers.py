from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
from SurveyLogic.PromptBuilders.ConstantPromptBuilder import ConstantPromptBuilder
from SurveyLogic.PromptBuilders.MonthlyFromFilePromptBuilder import MonthlyFromFilePromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.CommonProfilePromptBuilder import \
    CommonProfilePromptBuilder
from SurveyLogic.PromptBuilders.SystemPromptBuilder import SystemPromptBuilder
from SurveyLogic.PromptBuilders.Prompts import prompts
from SurveyLogic.PromptBuilders.TaskPromptBuilder import TaskPromptBuilder


def createSimplePromptBuilder() -> (BasePromptBuilder, BasePromptBuilder):
    builders = []

    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt))
    builders.append(TaskPromptBuilder(prompts.taskPrompt))

    headers = ['Основные параметры опроса и респондента', 'Задача']

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)

def createCustomPromptBuilder(useInflation: bool, usePolitics: bool) -> (BasePromptBuilder, BasePromptBuilder):
    builders = []
    headers = []
    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt))
    headers.append('Основные параметры опроса и респондента')

    if useInflation:
        builders.append(MonthlyFromFilePromptBuilder(prompts.inflationPath))
        headers.append('Основная информация об инфляции по РФ в целом за предыдущий месяц')

    if usePolitics:
        builders.append(MonthlyFromFilePromptBuilder(prompts.politicsPath))
        headers.append('Основная политико-экономическая информация по РФ в целом')

    builders.append(TaskPromptBuilder(prompts.taskPrompt))
    headers.append('Задача')

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)
