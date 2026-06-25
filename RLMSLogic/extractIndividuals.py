import pyreadstat
from tqdm import tqdm
import json
import numpy as np
import pandas as pd

pathToIndivisuals = '..\\data\\r33iall_84_DTA\\r33iall_84.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)


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

with open("rlms_2024_adult_profiles.jsonl", "w", encoding="utf-8") as f:
    for i, row in tqdm(df.iterrows(), total=len(df)):
        obj = {
            "row_number": int(i),
            "source": "RLMS-HSE",
            "year": 2024,
            "ids": {
                var: norm(row[var])
                for var in id_vars
                if var in row.index and not pd.isna(row[var])
            },
            "profile": row_to_profile(row),
        }

        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
