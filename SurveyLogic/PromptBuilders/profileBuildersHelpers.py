from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.CompositePromptBuilder import CompositePromptBuilder
from SurveyLogic.PromptBuilders.ConstantPromptBuilder import ConstantPromptBuilder
from SurveyLogic.PromptBuilders.ProfileSepcificPromptBuilders.CommonProfilePromptBuilder import \
    CommonProfilePromptBuilder
from SurveyLogic.PromptBuilders.SystemPromptBuilder import SystemPromptBuilder
from SurveyLogic.PromptBuilders.Prompts import prompts
from SurveyLogic.PromptBuilders.TaskPromptBuilder import TaskPromptBuilder


def createSimplePromptBuilder() -> (BasePromptBuilder, BasePromptBuilder):
    builders = []
    builders.append(CommonProfilePromptBuilder(prompts.respondentPrompt))
    builders.append(ConstantPromptBuilder(prompts.stateEconomyPrompt))
    builders.append(ConstantPromptBuilder(prompts.stateCommonPoliticalPrompt))
    builders.append(TaskPromptBuilder(prompts.taskPrompt))

    headers = ['Основные параметры опроса и респондента', 'Экономическая ситуация в России', 'Политическая ситуация в России и в мире', 'Задача']

    return SystemPromptBuilder(prompts.systemPrompt), CompositePromptBuilder(builders, headers)
