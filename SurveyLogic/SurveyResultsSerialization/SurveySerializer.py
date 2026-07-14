import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from SurveyLogic.SurveyResults.InflationSurveyRespond import InflationSurveyRespond
from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer


class SurveySerializer(BaseSurveySerializer):
    def __init__(self, profilesName: str, resultFolder: str):
        self.resultFolder = resultFolder
        self.profilesName = profilesName

    def saveSurvey(self, surveys: list[InflationSurveyRespond], surveyDate: date):
        targetFolder = Path(f'{self.resultFolder}//{self.profilesName}//{surveyDate.strftime("%d.%m.%Y")}')

        dir_path = Path(targetFolder)
        dir_path.mkdir(parents=True, exist_ok=True)

        for survey in surveys:
            self.__saveSingleSurvey(survey, targetFolder)

        return

    @staticmethod
    def __saveSingleSurvey(survey: InflationSurveyRespond, targetFolder: Path):
        filename = f'{survey.respondentId}.json'
        file_path = targetFolder / filename

        # Преобразуем датакласс в словарь и записываем в JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(survey), f, ensure_ascii=False, indent=2)
