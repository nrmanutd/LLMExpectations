from pathlib import Path

from Logging.BaseLogger import BaseLogger
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.AdditionalInformationSurveyExecutor import AdditionalInformationSurveyExecutor
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


def createSurveyRunner(profilesFolder: Path, systemPromptBuilder: BasePromptBuilder, promptBuilder: BasePromptBuilder, surveySerializer: BaseSurveySerializer, surveyer: BaseSurveyer, logger: BaseLogger) -> StandardSurveyRunner:
    profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
    surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
    surveyExecutor = AdditionalInformationSurveyExecutor(surveyExecutor)

    runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider, logger)
    return runner