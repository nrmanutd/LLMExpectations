import glob
import json
import os
import random
from dataclasses import asdict, fields
from pathlib import Path
from typing import List

import pyreadstat

from RLMSLogic.SimpleRLMSProfileConverter import SimpleRLMSProfileConverter
from RLMSLogic.RLMSProfileData import RLMSProfileData
from RLMSLogic.extractionHelpers import norm, value_to_label, safe_filename


class RLMSProfileExtractor:
    def __init__(self, converter: SimpleRLMSProfileConverter):
        self.converter = converter

    def extractAndSaveRLMSProfiles(self, dta_path: str, output_dir: str) -> List[RLMSProfileData]:
        """
        Загружает данные RLMS, извлекает профиль каждого респондента и сохраняет JSON-файлы.

        Аргументы:
            dta_path (str): путь к файлу .dta с данными RLMS.
            output_dir (str): путь к папке для сохранения JSON-файлов.
            year (int): год проведения опроса (используется для вычисления возраста).

        Возвращает:
            List[RLMSProfileData]: список объектов для всех респондентов.
        """
        # Чтение данных без применения меток (чтобы получить числовые коды)
        df, meta = pyreadstat.read_dta(
            dta_path,
            apply_value_formats=False,
            formats_as_category=False,
            user_missing=False
        )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        profiles = []

        for _, row in df.iterrows():
            # Идентификатор респондента
            respondent_id = norm(row.get('idind'))
            if respondent_id is None:
                continue  # пропускаем записи без id

            # Возраст: вычисляем из года рождения (переменная CCJ69.0)
            age = int(norm(row.get('cc_age')))

            # Пол (CCH5)
            sex = value_to_label('cch5', row.get('cch5'), meta)

            highestEducation = value_to_label('ccj72_18a', row.get('ccj72_18a'), meta)
            commonEducation = value_to_label('cc_educ', row.get('cc_educ'), meta)
            diploma = value_to_label('cc_diplom', row.get('cc_diplom'), meta)
            education = f'{diploma}, {commonEducation}, {highestEducation}'

            # Место рождения: комбинация ответов на вопросы 1-3
            loc_birth = value_to_label('cci1', row.get('cci1'), meta)  # другой/тот же
            country = value_to_label('cci2', row.get('cci2'), meta)
            place_type = value_to_label('cci3', row.get('cci3'), meta)
            parts = [p for p in (loc_birth, country, place_type) if p]
            LocalityOfBirth = ', '.join(parts)

            # Текущее место жительства – используем переменную s_type (тип поселения)
            localityStatus = value_to_label('status', row.get('status'), meta)
            psu = value_to_label('psu', row.get('psu'), meta)
            region = value_to_label('region', row.get('region'), meta)

            currentLocality = f'{localityStatus}, {psu}, {region}'
            typeOfPlace = localityStatus

            # Должность/профессия (вопрос 3: CCJ2_3a – должность, CCJ2_3b – профессия)
            occupation = value_to_label('cc_occup08', row.get('cc_occup08'), meta)
            numberOfEmployees = value_to_label('ccj13', row.get('ccj13'), meta)
            job = f'{occupation} (численность {numberOfEmployees})'

            # Отрасль (вопрос 6, CCJ5A)
            jobSector = value_to_label('ccj4_1', row.get('ccj4_1'), meta)

            # Зарплата: среднемесячная за 12 месяцев (вопрос 32, CCJ13)
            salary_raw = norm(row.get('ccj13_2'))
            salary = str(salary_raw) if salary_raw is not None else None

            # Сбережения: банковский депозит (вопрос 79.1, CCJ596.1)
            deposit = value_to_label('ccj596_1', row.get('ccj596_1'), meta)
            equities = value_to_label('ccj596_3', row.get('ccj596_3'), meta)
            brokerAccount = value_to_label('ccj596_4', row.get('ccj596_4'), meta)
            hasSavings = (deposit == 'Да' or equities == 'Да' or brokerAccount == 'Да')

            # Кредит: невыплаченный кредит (вопрос 79.2, CCJ596.2)
            credit_raw = value_to_label('ccj596_2', row.get('ccj596_2'), meta)
            hasCredit = (credit_raw == 'Да') if credit_raw is not None else False

            familyStatus = value_to_label('cc_marst', row.get('cc_marst'), meta)
            currentStatus = value_to_label('ccj1', row.get('ccj1'), meta)
            nationality = value_to_label('cci4', row.get('cci4'), meta)
            lastMonthSalary = str(norm(row.get('ccj60')))

            economicsSourceOfKnowledge = value_to_label('ccj597_1', row.get('ccj597_1'), meta)
            moneyStatusLastThreeYears = value_to_label('ccj60_5b', row.get('ccj60_5b'), meta)

            profile = RLMSProfileData(
                respondentId=str(respondent_id),
                age=age,
                sex=sex,
                education=education,
                LocalityOfBirth=LocalityOfBirth,
                currentLocality=currentLocality,
                typeOfLocality=typeOfPlace,
                job=job,
                jobSector=jobSector,
                salary=salary,
                hasSavings=hasSavings,
                hasCredit=hasCredit,
                familyStatus=familyStatus,
                currentStatus=currentStatus,
                nationality=nationality,
                lastMonthSalary=lastMonthSalary,
                economicsSourceOfKnowledge=economicsSourceOfKnowledge,
                moneyStatusLastThreeYears=moneyStatusLastThreeYears
            )

            # Сохраняем JSON
            filename = f"{safe_filename(respondent_id)}.json"
            filepath = output_path / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(profile), f, ensure_ascii=False, indent=2)

            profiles.append(profile)

        return profiles

    def generateAndSaveProfilesFromRLMS(self, rlmsProfilesFolder: str, targetFolder: str, fraction: float, seed: int = 42):
        pattern = os.path.join(rlmsProfilesFolder, "*.json")
        json_files = glob.glob(pattern)

        total = len(json_files)
        sample_size = int(fraction * total)

        if fraction > 0.0 and sample_size == 0:
            sample_size = 1

        sample_size = min(sample_size, total)

        # Случайная выборка без повторений
        random.seed(seed)
        selectedFiles = random.sample(json_files, sample_size)

        for f in selectedFiles:
            with open(f, 'r', encoding='utf-8') as ff:
                profile = json.load(ff)

            valid_field_names = {f.name for f in fields(RLMSProfileData)}
            filtered_data = {k: v for k, v in profile.items() if k in valid_field_names}

            profile = RLMSProfileData(**filtered_data)

            resultProfile = self.converter.convert(profile)

            folderPath = Path(targetFolder)
            folderPath.mkdir(parents=True, exist_ok=True)

            path = f'{targetFolder}//{resultProfile.respondentId}.json'
            with open(path, 'w', encoding='utf-8') as ff:
                json.dump(asdict(resultProfile), ff, ensure_ascii=False, indent=2)

