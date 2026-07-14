import numpy as np
import pandas as pd

def value_label(meta, col, value):
    """
    Расшифровывает значение через meta.variable_value_labels.
    Работает, если df был загружен с apply_value_formats=False.
    """
    if pd.isna(value):
        return np.nan

    labels = meta.variable_value_labels.get(col, {})
    if not labels:
        return value

    if value in labels:
        return labels[value]

    if isinstance(value, float) and value.is_integer() and int(value) in labels:
        return labels[int(value)]

    return value


def labeled_series(df, meta, col):
    if col not in df.columns:
        return pd.Series([np.nan] * len(df), index=df.index)

    return df[col].map(lambda x: value_label(meta, col, x))


def yes_no_code(x):
    """
    Для стандартных RLMS-вопросов:
    1 = Да
    2 = Нет
    """
    if pd.isna(x):
        return np.nan

    try:
        x = int(x)
    except Exception:
        return np.nan

    if x == 1:
        return "yes"
    if x == 2:
        return "no"

    return np.nan

def create_cat_df(work_df, meta):
    """
    Создает cat_df с перекодированными категориями под структуру ИнФОМ.

    На вход:
        work_df — DataFrame RLMS, уже отфильтрованный так, как тебе нужно
                  например, только репрезентативная выборка.
        meta — pyreadstat meta.

    На выход:
        cat_df — DataFrame с тем же index, где каждая колонка — аналитическая категория.
    """

    cat_df = pd.DataFrame(index=work_df.index)

    # ------------------------------------------------------------------
    # 1. Пол
    # ------------------------------------------------------------------
    if "cch5" in work_df.columns:
        sex = labeled_series(work_df, meta, "cch5").astype(str).str.upper()

        cat_df["Пол"] = np.select(
            [
                sex.str.contains("МУЖ", na=False),
                sex.str.contains("ЖЕН", na=False),
            ],
            [
                "мужчины",
                "женщины",
            ],
            default=None
        )
    else:
        cat_df["Пол"] = np.nan

    # ------------------------------------------------------------------
    # 2. Возраст
    # ------------------------------------------------------------------
    if "cc_age" in work_df.columns:
        age = pd.to_numeric(work_df["cc_age"], errors="coerce")

        cat_df["Возраст"] = pd.cut(
            age,
            bins=[17, 30, 45, 60, np.inf],
            labels=["18–30 лет", "31–45 лет", "46–60 лет", "старше 60 лет"],
            right=True
        ).astype("object")
    else:
        cat_df["Возраст"] = np.nan

    # ------------------------------------------------------------------
    # 3. Образование
    # ------------------------------------------------------------------
    def recode_education_from_ccj72_18a(x):
        """
        ccj72_18a — самый высокий уровень образования.

        Приводим к категориям ИнФОМ:
        - ниже среднего
        - среднее общее
        - среднее специальное
        - высшее
        """
        if pd.isna(x):
            return np.nan

        try:
            x = int(x)
        except Exception:
            return np.nan

        if x in [1]:
            return "ниже среднего"

        if x in [2]:
            return "среднее общее"

        if x in [3, 4, 5, 6, 15]:
            return "среднее специальное"

        if x in [10, 11, 12, 13, 14, 16, 17]:
            return "высшее"

        return np.nan

    if "ccj72_18a" in work_df.columns:
        cat_df["Образование"] = work_df["ccj72_18a"].map(recode_education_from_ccj72_18a)
    else:
        cat_df["Образование"] = np.nan

    # ------------------------------------------------------------------
    # 4. Род занятий
    # ------------------------------------------------------------------
    def recode_occupation_from_ccj90(x):
        """
        ccj90 — основной статус / занятие в настоящее время.
        """
        if pd.isna(x):
            return np.nan

        try:
            x = int(x)
        except Exception:
            return np.nan

        if x == 4:
            return "неработающие пенсионеры"

        if x == 8:
            return "не работают, но ищут работу"

        if x in [3, 5, 6, 7, 9]:
            return "не работают и не ищут работу"

        if x in [10, 11]:
            return "самозанятые"

        if x in [12, 13]:
            return "работающие по найму"

        # школьники/студенты — отдельной категории в твоем списке ИнФОМ нет
        if x in [1, 15, 16]:
            return "не работают и не ищут работу"

        if x == 14:
            return "другое"

        return np.nan

    if "ccj90" in work_df.columns:
        cat_df["Род занятий"] = work_df["ccj90"].map(recode_occupation_from_ccj90)
    else:
        cat_df["Род занятий"] = np.nan

    # ------------------------------------------------------------------
    # 5. Тип предприятия работодателя
    # ------------------------------------------------------------------
    if all(c in work_df.columns for c in ["ccj23", "ccj24", "ccj25"]):
        state_owner = work_df["ccj23"].map(yes_no_code)
        foreign_owner = work_df["ccj24"].map(yes_no_code)
        private_owner = work_df["ccj25"].map(yes_no_code)

        cat_df["Тип предприятия работодателя"] = np.select(
            [
                state_owner.eq("yes"),
                state_owner.eq("no") & (foreign_owner.eq("yes") | private_owner.eq("yes")),
                state_owner.eq("no") & foreign_owner.eq("no") & private_owner.eq("no"),
            ],
            [
                "государственное, с госучастием",
                "частное, НКО",
                "частное, НКО",
            ],
            default=None
        )
    else:
        cat_df["Тип предприятия работодателя"] = np.nan

    # ------------------------------------------------------------------
    # 6. Городское население трудоспособного возраста
    # ------------------------------------------------------------------
    if all(c in work_df.columns for c in ["status", "cc_age", "cch5"]):
        status_txt = labeled_series(work_df, meta, "status").astype(str).str.lower()
        sex_txt = labeled_series(work_df, meta, "cch5").astype(str).str.upper()
        age = pd.to_numeric(work_df["cc_age"], errors="coerce")

        is_urban = (
            status_txt.str.contains("город", na=False)
            | status_txt.str.contains("москва", na=False)
            | status_txt.str.contains("област", na=False)
        ) & ~status_txt.str.contains("село|деревн|пгт|пос[её]лок", na=False)

        # Можно поменять правило, если нужно использовать другой пенсионный возраст
        is_working_age = (
            (sex_txt.str.contains("ЖЕН", na=False) & age.between(18, 59, inclusive="both"))
            | (sex_txt.str.contains("МУЖ", na=False) & age.between(18, 64, inclusive="both"))
        )

        cat_df["Городское население трудоспособного возраста"] = np.where(
            is_urban & is_working_age,
            "городское население трудоспособного возраста",
            "прочие респонденты"
        )
    else:
        cat_df["Городское население трудоспособного возраста"] = np.nan

    # ------------------------------------------------------------------
    # 7. Доход на одного члена семьи
    # ------------------------------------------------------------------
    income_pc_candidates = [
        "income_per_capita",
        "hh_income_per_capita",
        "family_income_per_capita",
        "per_capita_income",
        "income_pc",
        "hh_income_pc",
    ]

    income_pc_col = next((c for c in income_pc_candidates if c in work_df.columns), None)

    if income_pc_col is not None:
        inc = pd.to_numeric(work_df[income_pc_col], errors="coerce")

        cat_df["Доход на одного члена семьи"] = pd.cut(
            inc,
            bins=[-np.inf, 17000, 22500, 33750, 50000, np.inf],
            labels=[
                "17000 руб. и менее",
                "17001–22500 руб.",
                "22501–33750 руб.",
                "33751–50000 руб.",
                "более 50000 руб.",
            ],
            right=True
        ).astype("object")
    else:
        cat_df["Доход на одного члена семьи"] = np.nan

    # ------------------------------------------------------------------
    # 8. Самооценка материального положения семьи
    # ------------------------------------------------------------------
    # Это прокси: удовлетворенность материальным положением.
    # Точной ИнФОМ-шкалы "денег не хватает на питание..." в adult-файле не видно.
    if "ccj66_1" in work_df.columns:
        cat_df["Самооценка материального положения семьи"] = labeled_series(work_df, meta, "ccj66_1")
    else:
        cat_df["Самооценка материального положения семьи"] = np.nan

    # ------------------------------------------------------------------
    # 9. Материальное положение семьи за год
    # ------------------------------------------------------------------
    # В RLMS вопрос про последние 3 года, не про 1 год.
    def recode_material_change(x):
        if pd.isna(x):
            return np.nan

        try:
            x = int(x)
        except Exception:
            return np.nan

        if x in [1, 2]:
            return "улучшилось"

        if x == 3:
            return "не изменилось"

        if x in [4, 5]:
            return "ухудшилось"

        return np.nan

    if "ccj60_5b" in work_df.columns:
        cat_df["Материальное положение семьи за год"] = work_df["ccj60_5b"].map(recode_material_change)
    else:
        cat_df["Материальное положение семьи за год"] = np.nan

    # ------------------------------------------------------------------
    # 10. Тип населенного пункта
    # ------------------------------------------------------------------
    def recode_settlement_type(row):
        status = str(row.get("status_label", "")).lower()
        region_txt = str(row.get("region_label", "")).lower()
        psu_txt = str(row.get("psu_label", "")).lower()

        popul = row.get("popul", np.nan)
        try:
            popul = float(popul)
        except Exception:
            popul = np.nan

        if "москва" in region_txt or "москва" in psu_txt:
            return "Москва"

        if "село" in status or "деревн" in status or "пгт" in status or "посел" in status:
            return "пгт, село"

        if pd.notna(popul):
            if popul >= 1_000_000:
                return "города 1 млн и более"
            if 500_000 <= popul < 1_000_000:
                return "города от 500 тыс. до 1 млн"
            if 100_000 <= popul < 500_000:
                return "города от 100 до 500 тыс."
            if popul < 100_000:
                return "города менее 100 тыс."

        return np.nan

    tmp_settle = pd.DataFrame(index=work_df.index)

    tmp_settle["popul"] = (
        pd.to_numeric(work_df["popul"], errors="coerce")
        if "popul" in work_df.columns
        else np.nan
    )

    tmp_settle["status_label"] = (
        labeled_series(work_df, meta, "status")
        if "status" in work_df.columns
        else ""
    )

    tmp_settle["region_label"] = (
        labeled_series(work_df, meta, "region")
        if "region" in work_df.columns
        else ""
    )

    tmp_settle["psu_label"] = (
        labeled_series(work_df, meta, "psu")
        if "psu" in work_df.columns
        else ""
    )

    cat_df["Тип населенного пункта"] = tmp_settle.apply(recode_settlement_type, axis=1)

    # ------------------------------------------------------------------
    # 11. Наличие сбережений
    # ------------------------------------------------------------------
    # Прокси: есть банковский депозит, вклад или накопительный счет.
    if "ccj596_1" in work_df.columns:
        dep = work_df["ccj596_1"].map(yes_no_code)

        cat_df["Наличие сбережений"] = np.select(
            [dep.eq("yes"), dep.eq("no")],
            ["есть", "нет"],
            default=None
        )
    else:
        cat_df["Наличие сбережений"] = np.nan

    # ------------------------------------------------------------------
    # 12. Наличие кредита
    # ------------------------------------------------------------------
    if "ccj596_2" in work_df.columns:
        cred = work_df["ccj596_2"].map(yes_no_code)

        cat_df["Наличие кредита"] = np.select(
            [cred.eq("yes"), cred.eq("no")],
            ["есть", "нет"],
            default=None
        )
    else:
        cat_df["Наличие кредита"] = np.nan

    # ------------------------------------------------------------------
    # 13. Предприятие закроется / перестанет существовать
    # ------------------------------------------------------------------
    # Прокси: беспокойство о потере работы.
    def recode_job_loss_fear(x):
        if pd.isna(x):
            return np.nan

        try:
            x = int(x)
        except Exception:
            return np.nan

        # Очень беспокоит / немного беспокоит / и да, и нет
        if x in [1, 2, 3]:
            return "есть опасения"

        # Не очень беспокоит / совсем не беспокоит
        if x in [4, 5]:
            return "нет опасений"

        return np.nan

    if "ccj31" in work_df.columns:
        cat_df["Предприятие, на котором работают, закроется/перестанет существовать"] = (
            work_df["ccj31"].map(recode_job_loss_fear)
        )
    else:
        cat_df["Предприятие, на котором работают, закроется/перестанет существовать"] = np.nan

    return cat_df

