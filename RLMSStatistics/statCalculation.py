import numpy as np
import pandas as pd
from pyreadstat import pyreadstat

from RLMSStatistics.csvTemplate import create_wide_stats_table
from RLMSStatistics.infoExtraction import create_cat_df

pathToIndivisuals = '..\\data\\r33iall_84_DTA\\r33iall_84.dta'

df, meta = pyreadstat.read_dta(
    pathToIndivisuals,
    apply_value_formats=False,
    formats_as_category=False,
    user_missing=False
)

work_df = df.copy()

if "cc_origsm" in work_df.columns:
    work_df = work_df[work_df["cc_origsm"] == 1].copy()

if "cc_inwgt" in work_df.columns:
    work_df = work_df[work_df["cc_inwgt"].notna()].copy()
    work_df = work_df[work_df["cc_inwgt"] > 0].copy()

cat_df = create_cat_df(work_df, meta)

def weighted_stats(
    cat_df,
    work_df,
    category_col,
    weight_col="cc_inwgt",
    category_name=None,
    ordered_options=None,
    include_missing=False
):
    tmp = pd.DataFrame(index=cat_df.index)
    tmp["option"] = cat_df[category_col]

    if weight_col in work_df.columns:
        tmp["weight"] = work_df.loc[cat_df.index, weight_col]
    else:
        tmp["weight"] = 1.0

    if not include_missing:
        tmp = tmp[tmp["option"].notna()].copy()

    if len(tmp) == 0:
        return pd.DataFrame([{
            "category": category_name or category_col,
            "option": "NOT_AVAILABLE",
            "n": 0,
            "share": np.nan,
            "weighted_n": np.nan,
            "weighted_share": np.nan,
        }])

    total_n = len(tmp)
    total_w = tmp["weight"].sum()

    out = (
        tmp
        .groupby("option", dropna=False)
        .agg(
            n=("option", "size"),
            weighted_n=("weight", "sum")
        )
        .reset_index()
    )

    out["share"] = out["n"] / total_n
    out["weighted_share"] = out["weighted_n"] / total_w if total_w != 0 else np.nan
    out["category"] = category_name or category_col

    out = out[["category", "option", "n", "share", "weighted_n", "weighted_share"]]

    if ordered_options is not None:
        order = {v: i for i, v in enumerate(ordered_options)}
        out["_order"] = out["option"].map(order).fillna(9999)
        out = out.sort_values(["_order", "option"]).drop(columns="_order")
    else:
        out = out.sort_values("weighted_share", ascending=False)

    return out.reset_index(drop=True)

category_orders = {
    "Пол": ["мужчины", "женщины"],
    "Возраст": ["18–30 лет", "31–45 лет", "46–60 лет", "старше 60 лет"],
    "Образование": ["ниже среднего", "среднее общее", "среднее специальное", "высшее"],
    "Род занятий": [
        "самозанятые",
        "неработающие пенсионеры",
        "не работают и не ищут работу",
        "не работают, но ищут работу",
        "работающие по найму",
        "другое",
    ],
    "Тип предприятия работодателя": [
        "государственное, с госучастием",
        "частное, НКО",
    ],
    "Городское население трудоспособного возраста": [
        "городское население трудоспособного возраста",
        "прочие респонденты",
    ],
    "Доход на одного члена семьи": [
        "17000 руб. и менее",
        "17001–22500 руб.",
        "22501–33750 руб.",
        "33751–50000 руб.",
        "более 50000 руб.",
    ],
    "Материальное положение семьи за год": [
        "улучшилось",
        "не изменилось",
        "ухудшилось",
    ],
    "Тип населенного пункта": [
        "Москва",
        "города 1 млн и более",
        "города от 500 тыс. до 1 млн",
        "города от 100 до 500 тыс.",
        "города менее 100 тыс.",
        "пгт, село",
    ],
    "Наличие сбережений": ["есть", "нет"],
    "Наличие кредита": ["есть", "нет"],
    "Предприятие, на котором работают, закроется/перестанет существовать": [
        "есть опасения",
        "нет опасений",
    ],
}

stats_parts = []

for category in cat_df.columns:
    stats_parts.append(
        weighted_stats(
            cat_df=cat_df,
            work_df=work_df,
            category_col=category,
            weight_col="cc_inwgt",
            category_name=category,
            ordered_options=category_orders.get(category),
            include_missing=False,
        )
    )

stats = pd.concat(stats_parts, ignore_index=True)

stats["share_pct"] = stats["share"] * 100
stats["weighted_share_pct"] = stats["weighted_share"] * 100

wide_stats = create_wide_stats_table(
    cat_df=cat_df,
    work_df=work_df,
    weight_col="cc_inwgt",
    skip_empty_categories=True,
)

print(wide_stats.shape)
print(wide_stats.head())

wide_stats.to_excel(
    "rlms_infom_like_stats_wide.xlsx",
    sheet_name="stats",
    merge_cells=True
)