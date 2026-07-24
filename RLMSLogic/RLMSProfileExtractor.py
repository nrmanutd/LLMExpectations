import glob
import json
import os
import re
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
        self.prefix = {33: 'cc', 32: 'bb', 31: 'aa', 30: 'z', 29: 'y', 28: 'x', 27: 'w', 26: 'v', 25: 'u', 24: 't', 23: 's'}

    def extractAndSaveRLMSProfiles(self, dta_path: Path, output_path: Path) -> List[RLMSProfileData]:
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
            str(dta_path),
            apply_value_formats=False,
            formats_as_category=False,
            user_missing=False
        )

        match = re.search(r'.*r(\d+)i.*', dta_path.name)
        waveNumber = int(match.group(1))
        p = self.prefix[waveNumber]

        output_path.mkdir(parents=True, exist_ok=True)

        profiles = []

        for _, row in df.iterrows():
            # Идентификатор респондента
            respondent_id = norm(row.get('idind'))
            if respondent_id is None:
                continue  # пропускаем записи без id

            # Возраст: вычисляем из года рождения (переменная CCJ69.0)
            age = norm(row.get(f'{p}_age'))

            # Пол (CCH5)
            sex = value_to_label(f'{p}h5', row.get(f'{p}h5'), meta)

            highestEducation = value_to_label(f'{p}j72_18a', row.get(f'{p}j72_18a'), meta)
            commonEducation = value_to_label(f'{p}_educ', row.get(f'{p}_educ'), meta)
            diploma = value_to_label(f'{p}_diplom', row.get(f'{p}_diplom'), meta)
            education = f'{diploma}, {commonEducation}, {highestEducation}'

            # Место рождения: комбинация ответов на вопросы 1-3
            loc_birth = value_to_label(f'{p}i1', row.get(f'{p}i1'), meta)  # другой/тот же
            country = value_to_label(f'{p}i2', row.get(f'{p}i2'), meta)
            place_type = value_to_label(f'{p}i3', row.get(f'{p}i3'), meta)
            parts = [p for p in (loc_birth, country, place_type) if p]
            LocalityOfBirth = ', '.join(parts)

            # Текущее место жительства – используем переменную s_type (тип поселения)
            localityStatus = value_to_label('status', row.get('status'), meta)
            psu = value_to_label('psu', row.get('psu'), meta)
            region = value_to_label('region', row.get('region'), meta)

            currentLocality = f'{localityStatus}, {psu}, {region}'
            typeOfPlace = localityStatus

            # Должность/профессия (вопрос 3: CCJ2_3a – должность, CCJ2_3b – профессия)
            occupation = value_to_label(f'{p}_occup08', row.get(f'{p}_occup08'), meta)
            numberOfEmployees = value_to_label(f'{p}j13', row.get(f'{p}j13'), meta)
            job = f'{occupation} (численность {numberOfEmployees})'

            # Отрасль (вопрос 6, CCJ5A)
            jobSector = value_to_label(f'{p}j4_1', row.get(f'{p}j4_1'), meta)

            # Зарплата: среднемесячная за 12 месяцев (вопрос 32, CCJ13)
            salary_raw = norm(row.get(f'{p}j13_2'))
            salary = str(salary_raw) if salary_raw is not None else None

            # Сбережения: банковский депозит (вопрос 79.1, CCJ596.1)
            deposit = value_to_label(f'{p}j596_1', row.get(f'{p}j596_1'), meta)
            equities = value_to_label(f'{p}j596_3', row.get(f'{p}j596_3'), meta)
            brokerAccount = value_to_label(f'{p}j596_4', row.get(f'{p}j596_4'), meta)
            hasSavings = (deposit == 'Да' or equities == 'Да' or brokerAccount == 'Да')

            # Кредит: невыплаченный кредит (вопрос 79.2, CCJ596.2)
            credit_raw = value_to_label(f'{p}j596_2', row.get(f'{p}j596_2'), meta)
            hasCredit = (credit_raw == 'Да') if credit_raw is not None else False

            familyStatus = value_to_label(f'{p}_marst', row.get(f'{p}_marst'), meta)
            currentStatus = value_to_label(f'{p}j1', row.get(f'{p}j1'), meta)
            nationality = value_to_label(f'{p}i4', row.get(f'{p}i4'), meta)
            lastMonthSalary = str(norm(row.get(f'{p}j60')))

            currentSources = []
            for i in range(1, 11):
                curLabel = f'{p}j597_{i}'
                curValue = value_to_label(curLabel, row.get(curLabel), meta)
                if curValue is not None:
                    currentSources.append(curValue)

            economicsSourceOfKnowledge = ','.join(currentSources)
            moneyStatusLastThreeYears = value_to_label(f'{p}j60_5b', row.get(f'{p}j60_5b'), meta)

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

    def generateAndSaveProfilesFromRLMS(self, rlmsProfilesFolder: Path, folderPath: Path, sample_size: int, adultAge: int, seed: int = 42):
        pattern = os.path.join(str(rlmsProfilesFolder), "*.json")
        json_files = glob.glob(pattern)

        total = len(json_files)
        if sample_size <= 0 or sample_size > total:
            raise ValueError(f'Incorrect value of sample size: {sample_size}, it should be 0 < {sample_size} <= {total}')

        # Случайная выборка без повторений
        random.seed(seed)
        selectedFiles = random.sample(json_files, len(json_files))

        counter = 0

        for f in selectedFiles:
            if counter >= sample_size:
                break

            with open(f, 'r', encoding='utf-8') as ff:
                profile = json.load(ff)

            valid_field_names = {f.name for f in fields(RLMSProfileData)}
            filtered_data = {k: v for k, v in profile.items() if k in valid_field_names}

            profile = RLMSProfileData(**filtered_data)
            resultProfile = self.converter.convert(profile)

            if resultProfile.age < adultAge:
                continue

            folderPath.mkdir(parents=True, exist_ok=True)

            path = folderPath / f'{resultProfile.respondentId}.json'
            with open(path, 'w', encoding='utf-8') as ff:
                json.dump(asdict(resultProfile), ff, ensure_ascii=False, indent=2)

            counter = counter + 1

