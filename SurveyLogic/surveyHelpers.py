import shutil
from datetime import datetime

import pandas as pd
from pathlib import Path

from Logging.BaseLogger import BaseLogger
from SurveyLogic.AsyncSurveyRunner import AsyncSurveyRunner
from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileDataLoader import ProfileDataLoader
from SurveyLogic.PromptBuilders.Profiles.RandomSubsampleProfilesProvider import RandomSubsampleProfilesProvider
from SurveyLogic.PromptBuilders.Profiles.StandardProfilesProvider import StandardProfilesProvider
from SurveyLogic.StandardSurveyRunner import StandardSurveyRunner
from SurveyLogic.SurveyExecution.AdditionalInformationSurveyExecutor import AdditionalInformationSurveyExecutor
from SurveyLogic.SurveyExecution.StandardAsyncSurveyExecutor import StandardAsyncSurveyExecutor
from SurveyLogic.SurveyExecution.StandardSurveyExecutor import StandardSurveyExecutor
from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer
from SurveyLogic.Surveyers.AsyncSurveyer import AsyncSurveyer
from SurveyLogic.Surveyers.BaseSurveyer import BaseSurveyer


def createSurveyRunner(profilesFolder: Path, systemPromptBuilder: BasePromptBuilder, promptBuilder: BasePromptBuilder, surveySerializer: BaseSurveySerializer, surveyer: BaseSurveyer, logger: BaseLogger) -> StandardSurveyRunner:
    profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
    surveyExecutor = StandardSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
    surveyExecutor = AdditionalInformationSurveyExecutor(surveyExecutor)

    runner = StandardSurveyRunner(surveySerializer, surveyExecutor, profilesProvider, logger)
    return runner

def createAsyncSurveyRunner(profilesFolder: Path, systemPromptBuilder: BasePromptBuilder, promptBuilder: BasePromptBuilder, surveySerializer: BaseSurveySerializer, surveyer: AsyncSurveyer, profilesCount: int, logger: BaseLogger) -> AsyncSurveyRunner:
    profilesProvider = StandardProfilesProvider(profilesFolder, ProfileDataLoader())
    profilesProvider = RandomSubsampleProfilesProvider(profilesProvider, profilesCount)
    surveyExecutor = StandardAsyncSurveyExecutor(systemPromptBuilder, promptBuilder, surveyer)
    #surveyExecutor = AdditionalInformationSurveyExecutor(surveyExecutor)

    runner = AsyncSurveyRunner(surveySerializer, surveyExecutor, profilesProvider, logger)
    return runner

def getDatesRowWithMonthlyStep(start: str, end: str):
    return pd.date_range(start=start, end=end, freq='MS', inclusive='both').tolist()

def getDatesRowWithWeeklyStep(start: str, end: str):
    return pd.date_range(start=start, end=end, freq='7D', inclusive='both').tolist()

def extractDatesFromFile(path: Path) -> list[datetime]:
    df = pd.read_excel(path, sheet_name=0, header=0)

    # Получаем заголовки (первая строка)
    headers = df.columns.tolist()

    # Парсим каждую дату
    parsed_dates = []
    for header in headers:
        dt = header.to_pydatetime()
        parsed_dates.append(dt)

    parsed_dates.sort()

    return parsed_dates

def copyPromptTemplatesToFolder(promptFolder: Path, resultsFolder: Path):
    if resultsFolder.exists():
        shutil.rmtree(resultsFolder)
    resultsFolder.mkdir(parents=True, exist_ok=True)

    # Находим все .txt файлы
    txt_files = list(promptFolder.glob('*.txt'))

    # Копируем каждый файл
    for file_path in txt_files:
        dst_path = resultsFolder / file_path.name
        shutil.copy2(file_path, dst_path)  # copy2 сохраняет метаданные

