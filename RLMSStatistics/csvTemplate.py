import numpy as np
import pandas as pd
from pathlib import Path

def create_wide_stats_table(
    cat_df,
    work_df=None,
    weight_col="cc_inwgt",
    skip_empty_categories=True,
):
    """
    Делает широкую таблицу статистики:

    columns:
        level 0 = категория
        level 1 = вариант ответа

    rows:
        n
        share_pct
        weighted_n
        weighted_share_pct

    cat_df — результат create_cat_df(work_df, meta)
    work_df — исходный DataFrame с весами
    """

    category_orders = {
        "Пол": [
            "мужчины",
            "женщины",
        ],
        "Возраст": [
            "18–30 лет",
            "31–45 лет",
            "46–60 лет",
            "старше 60 лет",
        ],
        "Образование": [
            "ниже среднего",
            "среднее общее",
            "среднее специальное",
            "высшее",
        ],
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
        "Самооценка материального положения семьи": [
            "Полностью удовлетворены",
            "Скорее удовлетворены",
            "И да, и нет",
            "Не очень удовлетворены",
            "Совсем не удовлетворены",
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
        "Наличие сбережений": [
            "есть",
            "нет",
        ],
        "Наличие кредита": [
            "есть",
            "нет",
        ],
        "Предприятие, на котором работают, закроется/перестанет существовать": [
            "есть опасения",
            "нет опасений",
        ],
    }

    if work_df is not None and weight_col in work_df.columns:
        weights = pd.to_numeric(work_df.loc[cat_df.index, weight_col], errors="coerce")
    else:
        weights = pd.Series(1.0, index=cat_df.index)

    result = {}

    # Население в целом
    valid_weight = weights.notna()
    total_n_all = len(cat_df)
    total_w_all = weights[valid_weight].sum()

    result[("Население в целом", "Всего")] = {
        "n": total_n_all,
        "share_pct": 100.0,
        "weighted_n": total_w_all,
        "weighted_share_pct": 100.0,
    }

    for category in cat_df.columns:
        s = cat_df[category]

        if skip_empty_categories and s.notna().sum() == 0:
            continue

        tmp = pd.DataFrame({
            "option": s,
            "weight": weights,
        })

        tmp = tmp[tmp["option"].notna()].copy()

        if len(tmp) == 0:
            continue

        total_n = len(tmp)
        total_w = tmp["weight"].sum()

        ordered_options = category_orders.get(category)

        if ordered_options is None:
            options = list(tmp["option"].dropna().unique())
        else:
            options = list(ordered_options)

        for option in options:
            mask = tmp["option"] == option

            n = int(mask.sum())
            weighted_n = tmp.loc[mask, "weight"].sum()

            result[(category, option)] = {
                "n": n,
                "share_pct": n / total_n * 100 if total_n > 0 else np.nan,
                "weighted_n": weighted_n,
                "weighted_share_pct": weighted_n / total_w * 100 if total_w > 0 else np.nan,
            }

        # Если появились варианты, которых нет в order, тоже добавим в конец
        if ordered_options is not None:
            extra_options = [
                x for x in tmp["option"].dropna().unique()
                if x not in ordered_options
            ]

            for option in extra_options:
                mask = tmp["option"] == option

                n = int(mask.sum())
                weighted_n = tmp.loc[mask, "weight"].sum()

                result[(category, option)] = {
                    "n": n,
                    "share_pct": n / total_n * 100 if total_n > 0 else np.nan,
                    "weighted_n": weighted_n,
                    "weighted_share_pct": weighted_n / total_w * 100 if total_w > 0 else np.nan,
                }

    wide = pd.DataFrame(result).T.T

    wide.index = [
        "Количество респондентов",
        "Доля, %",
        "Взвешенное количество",
        "Взвешенная доля, %",
    ]

    wide.columns = pd.MultiIndex.from_tuples(wide.columns)

    return wide