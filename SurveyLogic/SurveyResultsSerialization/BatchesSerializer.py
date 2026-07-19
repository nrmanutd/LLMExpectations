import json
from datetime import date
from pathlib import Path

from SurveyLogic.SurveyResultsSerialization.BaseSurveySerializer import BaseSurveySerializer


class BatchesSerializer(BaseSurveySerializer):
    def __init__(self, subFolderName: str, resultFolder: str):
        self.resultFolder = resultFolder
        self.subFolderName = subFolderName

    def saveSurvey(self, survey: list[str], surveyDate: date):
        targetFolder = Path(f'{self.resultFolder}//{self.subFolderName}')

        dir_path = Path(targetFolder)
        dir_path.mkdir(parents=True, exist_ok=True)

        filename = f'{self.subFolderName}_{surveyDate.strftime('%d.%m.%Y')}.jsonl'
        file_path = targetFolder / filename

        with open(file_path, "w", encoding="utf-8") as f:
            for req in survey:
                f.write(json.dumps(req, ensure_ascii=False) + "\n")

        return
