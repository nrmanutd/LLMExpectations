import re
from datetime import date
from pathlib import Path

from SurveyLogic.PromptBuilders.BasePromptBuilder import BasePromptBuilder
from SurveyLogic.PromptBuilders.Profiles.ProfileData import ProfileData


class MonthlyFromFilePromptBuilder(BasePromptBuilder):
    def __init__(self, dataFolder: str):
        self.dataFolder = dataFolder
        self.monthNames = {
            1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель",
            5: "Май", 6: "Июнь", 7: "Июль", 8: "Август",
            9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
        }

    def buildPrompt(self, surveyDate: date, profile: ProfileData) -> str:
        # Определяем предыдущий месяц и год
        if surveyDate.month == 1:
            prev_month = 12
            prev_year = surveyDate.year - 1
        else:
            prev_month = surveyDate.month - 1
            prev_year = surveyDate.year

        target_month_name = self.monthNames[prev_month]
        file_path = Path(self.dataFolder) / f"{prev_year}.txt"

        if not file_path.exists():
            raise ValueError(f'File {file_path} doesnt exist')

        # Читаем содержимое файла

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Ищем текст между {Месяц} и следующим { или до конца строки
        # Шаблон: ищем метку, затем захватываем всё до следующей открывающей фигурной скобки
        pattern = re.compile(
            r"{" + re.escape(target_month_name) + r"}(.*?)(?=\{\w+}|$)",
            re.DOTALL
        )
        match = pattern.search(content)

        if match:
            return match.group(1).strip()
        else:
            raise ValueError('Incorrect format of inflation file')