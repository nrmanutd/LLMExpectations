import json
import re
from pathlib import Path

import pandas as pd
import pyreadstat
from tqdm import tqdm

from RLMSLogic.extractionHelpers import value_to_label, norm

pathToIndivisuals = '..\\data\\RLMS waves\\r33i_os_84.dta'
pathToHH = '..\\data\\RLMS waves\\r33h_os_83.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

dfhh, metahh = pyreadstat.read_dta(
    pathToHH,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

for __, irow in df.iterrows():
    continue
    id = irow['ccid_h']

    matched = False
    for _, hhrow in dfhh.iterrows():
        hhId = hhrow['ccid_h']
        if id == hhId:
            print(f'Id = {id} matched, member id = {irow['ccid_i']}, unique member = {irow['idind']}')
            print(f'Individual: {irow['region']}, {irow['psu']}, {irow['site']}, family # {irow['cch3']}, individual # {irow['cch4']}')
            print(f'Household: answering {hhrow['cca8']}, {hhrow['region'], hhrow['psu'], hhrow['site']}, членов семьи {hhrow['cc_nfm']}, family # {hhrow['cca3']}')

            members = hhrow['cc_nfm']
            print(f'1 member: {hhrow['ccidind1']}')
            if members >= 2:
                print(f'2 member: {hhrow['ccidind2']}')
            if members >= 3:
                print(f'3 member: {hhrow['ccidind3']}')
            if members >= 4:
                print(f'4 member: {hhrow['ccidind4']}')

            matched = True

    print(f'Matched hh and ind: {matched}')

a = df.columns
for s in ['psu']:
    print(s)
    print(df[s][0])

    print(meta.variable_value_labels[s])
    print(meta.column_names_to_labels[s])
    #print(meta.value_labels[s])

with open('column_names_households.txt', 'w', encoding='utf-8') as f:
    for col in dfhh.columns:
        f.write(col + '\n')

with open('questions_households.txt', 'w', encoding='utf-8') as f:
    row = dfhh.iloc[0]
    for var, raw in row.items():
        question = meta.column_names_to_labels.get(var, var)
        f.write(f'Code = {var}, Question = {question}' + '\n')

#print(df.columns)
#print(f'{int(df['status'][0])}')
#print(df)

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

def row_to_profile(row, meta):
    profile = {}
    excludedQuestions = ['номер индивида',
    'идентификационная переменная']

    for var, raw in row.items():
        answer = value_to_label(var, raw, meta)

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

id_vars = ['ccid_h', 'ccredid_h']
person = {
    "ids": {
        var: norm(df.iloc[0][var])
        for var in id_vars
    },
    "profile": row_to_profile(df.iloc[0], meta)
}

print(person)

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
            "profile": row_to_profile(row, meta),
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