import pyreadstat
from tqdm import tqdm
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd

pathToIndivisuals = '..\\data\\r33iall_84_DTA\\r33iall_84.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)
a = df.columns
for s in ['ccj597_1']:
    print(s)
    print(df[s][0])

    print(meta.variable_value_labels[s])
    print(meta.column_names_to_labels[s])
    #print(meta.value_labels[s])

with open('column_names.txt', 'w', encoding='utf-8') as f:
    for col in df.columns:
        f.write(col + '\n')

#print(df.columns)
#print(f'{int(df['status'][0])}')
#print(df)


def norm(x):
    if pd.isna(x):
        return None
    if isinstance(x, (np.integer, np.floating)):
        return x.item()
    return x


def value_to_label(var, value):
    value = norm(value)
    if value is None:
        return None

    labels = meta.variable_value_labels.get(var, {})
    if not labels:
        return value

    if value in labels:
        return labels[value]

    if isinstance(value, float) and value.is_integer() and int(value) in labels:
        return labels[int(value)]

    return value

def show_person(row_number=0, max_vars=80):
    row = df.iloc[row_number]
    id_vars = ['idind', 'region']

    print("IDS:")
    for var in id_vars:
        print(f"{var}: {row[var]}")

    print("\nPROFILE:")
    shown = 0

    for var, raw in row.items():
        if var in id_vars:
            continue

        answer = value_to_label(var, raw)
        if answer is None:
            continue

        question = meta.column_names_to_labels.get(var, var)

        print(f"\n[{var}] {question}")
        print(f"answer: {answer}")
        print(f"raw: {raw}")

        shown += 1
        if shown >= max_vars:
            break

def row_to_profile(row):
    profile = {}
    excludedQuestions = ['номер индивида',
    'идентификационная переменная']

    for var, raw in row.items():
        answer = value_to_label(var, raw)

        if answer is None:
            continue

        question = meta.column_names_to_labels.get(var, var)

        shouldOmit = False
        for excludedQuestion in excludedQuestions:
            if excludedQuestion in question.lower():
                shouldOmit = True
                break

        if shouldOmit:
            continue

        profile[var] = {
            "question": question,
            "answer": answer,
            "raw_value": norm(raw),
        }

    return profile

id_vars = ['idind', 'region']
person = {
    "ids": {
        var: norm(df.iloc[0][var])
        for var in id_vars
    },
    "profile": row_to_profile(df.iloc[0])
}

def safe_filename_part(x):
    x = str(x)
    x = x.strip()
    x = re.sub(r"[^\w\-]+", "_", x, flags=re.UNICODE)
    x = re.sub(r"_+", "_", x)
    return x.strip("_")

def safe_filename_part(x):
    x = str(x)
    x = x.strip()
    x = re.sub(r"[^\w\-]+", "_", x, flags=re.UNICODE)
    x = re.sub(r"_+", "_", x)
    return x.strip("_")


def make_respondent_filename(row, row_number, id_vars):
    """
    Формирует имя файла.
    Если есть idind — используем его.
    Если нет — используем row_number.
    """
    ids = {}

    for var in id_vars:
        if var in row.index and not pd.isna(row[var]):
            ids[var.lower()] = norm(row[var])

    if "idind" in ids:
        base = f"respondent_idind_{safe_filename_part(ids['idind'])}"
    elif "id_w" in ids:
        base = f"respondent_idw_{safe_filename_part(ids['id_w'])}"
    else:
        base = f"respondent_row_{row_number:06d}"

    return f"{base}.json"

def export_respondents_to_separate_json_files(
    df,
    meta,
    out_dir,
    id_vars,
    year=2024,
    include_ids=True,
    overwrite=True,
):
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)

    saved_files = []

    for row_number, (_, row) in enumerate(tqdm(df.iterrows(), total=len(df))):
        filename = make_respondent_filename(row, row_number, id_vars)
        path = out_dir / filename

        if path.exists() and not overwrite:
            # чтобы не перезаписать, добавляем row_number
            path = out_dir / f"respondent_row_{row_number:06d}_{filename}"

        ids = {
            var: norm(row[var])
            for var in id_vars
            if var in row.index and not pd.isna(row[var])
        }

        obj = {
            "row_number": row_number,
            "source": "RLMS-HSE",
            "year": year,
            "profile": row_to_profile(row),
        }

        if include_ids:
            obj["ids"] = ids

        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)

        saved_files.append(str(path))

    return saved_files

#OUT_DIR = Path("..\\data\\rlms_2024_adult_respondents_json")
#OUT_DIR.mkdir(exist_ok=True)
#saved_files = export_respondents_to_separate_json_files(
#   df=df,
#    meta=meta,
#    out_dir=OUT_DIR,
#    id_vars=id_vars,
#    year=2024,
#    include_ids=True,
#    overwrite=True,
#)

#print("Saved files:", len(saved_files))
#print("Example:", saved_files[0])