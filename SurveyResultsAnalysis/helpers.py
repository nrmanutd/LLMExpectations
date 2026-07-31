import json
import os
from datetime import datetime

import pandas as pd

from SurveyLogic.SurveyResults.InflationSurveyRespond import InflationSurveyRespond

def load_from_official_statistics_1m(fileName):
    directEstimations = pd.read_excel(fileName, index_col=0)
    directEstimations = directEstimations.T
    directEstimations.index = pd.to_datetime(directEstimations.index)

    return directEstimations

def load_respond_from_json(file_path: str) -> InflationSurveyRespond:
    """Загружает объект InflationSurveyRespond из JSON-файла"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Создаем объект, распаковывая словарь
    return InflationSurveyRespond(**data)

def getCategory(answeredCategory: str, type: str):
    if answeredCategory == 'вырастут очень сильно' or answeredCategory == 'high_growth':
        return 'вырастут очень сильно' if type == 'expected' else 'выросли очень сильно'

    if answeredCategory == 'вырастут умеренно' or answeredCategory == 'medium_growth':
        return 'вырастут умеренно' if type == 'expected' else 'выросли умеренно'

    if answeredCategory == 'вырастут незначительно' or answeredCategory == 'little_growth':
        return 'вырастут незначительно' if type == 'expected' else 'выросли незначительно'

    if answeredCategory == 'не изменятся' or answeredCategory == 'no_change':
        return 'не изменятся' if type == 'expected' else 'не изменились'

    if answeredCategory == 'снизились' or answeredCategory == 'снизятся':
        return 'снизятся' if type == 'expected' else 'снизились'

    if answeredCategory == 'no_answer':
        return 'затрудняюсь ответить'

    if answeredCategory == 'выросли умеренно' or answeredCategory == 'выросли очень сильно' or answeredCategory == 'выросли незначительно' or answeredCategory == 'не изменились' or answeredCategory == 'затрудняюсь ответить' or answeredCategory == 'снизятся':
        return answeredCategory

    if answeredCategory == 'снизились' or answeredCategory == 'снизлись' or answeredCategory == 'снизился' or answeredCategory == 'снизилась':
        return 'снизились'

    if answeredCategory == 'снизился незначительно':
        return 'снизились незначительно'

    if answeredCategory is None:
        return None

    raise ValueError(f'Unknown answer category: {answeredCategory}')

def load_pdtable(folder: str):
    files = os.listdir(folder)
    files = [f for f in files if os.path.isfile(os.path.join(folder, f))]

    rows = []
    for file in files:
        respond = load_respond_from_json(f'{folder}/{file}')

        expectedCategory = getCategory(respond.expected_inflation_1m_pct, 'expected')
        observableCategory = getCategory(respond.observable_inflation_last_1m_pct, 'observable')

        if expectedCategory is None or observableCategory is None:
            continue

        if respond.expected_inflation_12m_pct is None or respond.observable_inflation_12m_pct is None:
            continue

        rows.append({
            'date': datetime.strptime(respond.target_date, "%d.%m.%Y"),
            'expected_12m': float(respond.expected_inflation_12m_pct),
            'observable_12m': float(respond.observable_inflation_12m_pct),
            'expected_1m': expectedCategory,
            'observable_1m': observableCategory
        })

    return pd.DataFrame(rows)

def load_pdtable_with_repeats(folder: str):
    dates = pd.date_range(start='2016-01-01', end='2026-01-01', freq='QS', inclusive='both').tolist()
    files = os.listdir(folder)
    files = [f for f in files if os.path.isfile(os.path.join(folder, f))]

    rows = []
    for file in files:
        respond = load_respond_from_json(f'{folder}/{file}')

        expectedCategory = getCategory(respond.expected_inflation_1m_pct, 'expected')
        observableCategory = getCategory(respond.observable_inflation_last_1m_pct, 'observable')

        if expectedCategory is None or observableCategory is None:
            continue

        if respond.expected_inflation_12m_pct is None or respond.observable_inflation_12m_pct is None:
            continue

        for d in dates:
            rows.append({
                'date': d,
                'expected_12m': float(respond.expected_inflation_12m_pct),
                'observable_12m': float(respond.observable_inflation_12m_pct),
                'expected_1m': expectedCategory,
                'observable_1m': observableCategory
            })

    return pd.DataFrame(rows)

def load_from_official_statistics(fileName):
    directEstimations = pd.read_excel(fileName, index_col=0)
    directEstimations.rename(
        index={
            'наблюдаемая инфляция (в %)': 'observable_inflation',  # замените на точное название из файла
            'ожидаемая инфляция (в %)': 'expected_inflation'  # замените на точное название из файла
        },
        inplace=True
    )
    directEstimations = directEstimations.T
    directEstimations.index = pd.to_datetime(directEstimations.index)

    return directEstimations

def aggregate_survey(surveys):
    quarterly_agg_df = surveys.groupby('date').agg({
        'observable_12m': ['mean', 'std', 'count'],
        'expected_12m': ['mean', 'std', 'count']
    }).reset_index()

    # Переименовываем колонки
    quarterly_agg_df.columns = ['date', 'obs_mean', 'obs_std', 'obs_count',
                                'exp_mean', 'exp_std', 'exp_count']

    print("\nАгрегированные квартальные данные (первые 5):")
    print(quarterly_agg_df.head())
    return quarterly_agg_df


def aggregate_to_percentages(df, date_col='date', response_col='response', categories=None):
    """
    Агрегирует неагрегированные данные в формат процентов

    Args:
        df: DataFrame с колонками date и response
        date_col: название колонки с датами
        response_col: название колонки с ответами
        categories: список категорий (если None, определяется автоматически)

    Returns:
        DataFrame с датами в индексе и категориями в колонках
    """
    # Если категории не указаны, определяем автоматически
    if categories is None:
        categories = sorted(df[response_col].unique())

    # Группируем по дате и ответу
    grouped = df.groupby([date_col, response_col]).size().reset_index(name='count')

    # Получаем общее количество для каждой даты
    total_per_date = grouped.groupby(date_col)['count'].sum().reset_index(name='total')

    # Объединяем
    grouped = grouped.merge(total_per_date, on=date_col)

    # Вычисляем проценты
    grouped['pct'] = (grouped['count'] / grouped['total']) * 100

    # Создаем сводную таблицу
    pivot = grouped.pivot(index=date_col, columns=response_col, values='pct').fillna(0)

    # Убеждаемся, что все категории присутствуют
    for cat in categories:
        if cat not in pivot.columns:
            pivot[cat] = 0

    # Приводим к целым числам
    pivot = pivot.round().astype(int)

    # Корректируем сумму до 100
    for idx in pivot.index:
        diff = 100 - pivot.loc[idx].sum()
        if diff != 0:
            # Добавляем разницу к первой категории
            pivot.loc[idx, pivot.columns[0]] += diff

    return pivot


from scipy.stats import chi2_contingency, wasserstein_distance
import numpy as np


def safe_chi2_contingency(obs, correction=True):
    """
    Безопасная версия chi2_contingency с обработкой нулевых ожидаемых частот

    Args:
        obs: таблица сопряженности (2 x n_categories)
        correction: использовать ли поправку Йейтса

    Returns:
        chi2_stat, p_value, dof, expected
    """
    # Проверяем, есть ли категории с нулями в обоих распределениях
    obs = np.array(obs)

    # Находим категории, где сумма по строке равна 0
    zero_categories = np.where(obs.sum(axis=0) == 0)[0]

    if len(zero_categories) > 0:
        print(f"⚠️ Найдены категории с нулевыми значениями: {zero_categories}")
        # Удаляем нулевые категории
        obs_filtered = np.delete(obs, zero_categories, axis=1)

        if obs_filtered.shape[1] < 2:
            print("⚠️ Слишком мало категорий для теста")
            return np.nan, np.nan, 0, None

        # Пробуем снова с отфильтрованными данными
        try:
            return chi2_contingency(obs_filtered, correction=correction)
        except ValueError:
            # Если все еще ошибка, используем альтернативный подход
            print("⚠️ Использую альтернативный подход...")
            return alternative_chi2_test(obs)
    else:
        try:
            return chi2_contingency(obs, correction=correction)
        except ValueError as e:
            if "zero element" in str(e):
                print("⚠️ Ошибка с нулевыми ожидаемыми частотами, использую альтернативный подход...")
                return alternative_chi2_test(obs)
            else:
                raise


def alternative_chi2_test(obs):
    """
    Альтернативный тест для таблиц с нулевыми значениями
    Использует G-тест (отношение правдоподобия) вместо хи-квадрат
    """
    obs = np.array(obs)

    # Удаляем категории с нулевыми суммами
    valid_cols = obs.sum(axis=0) > 0
    obs = obs[:, valid_cols]

    if obs.shape[1] < 2:
        return np.nan, np.nan, 0, None

    # Рассчитываем ожидаемые частоты
    row_totals = obs.sum(axis=1, keepdims=True)
    col_totals = obs.sum(axis=0, keepdims=True)
    total = obs.sum()

    expected = (row_totals * col_totals) / total

    # Заменяем нулевые ожидаемые частоты на очень маленькое число
    expected = np.maximum(expected, 1e-10)

    # G-тест (отношение правдоподобия)
    # G = 2 * sum(obs * log(obs / expected))
    with np.errstate(divide='ignore', invalid='ignore'):
        ratio = obs / expected
        ratio = np.where(ratio == 0, 1e-10, ratio)  # Заменяем нули
        g_stat = 2 * np.sum(obs * np.log(ratio))

    # p-value из хи-квадрат распределения
    dof = (obs.shape[0] - 1) * (obs.shape[1] - 1)
    from scipy.stats import chi2
    p_value = 1 - chi2.cdf(g_stat, dof)

    return g_stat, p_value, dof, expected


def compare_distributions_robust(monthly, quarterly, categories):
    """
    Сравнивает два распределения с робастной обработкой нулей
    """
    # Проверяем, есть ли категории с нулями
    monthly = np.array(monthly)
    quarterly = np.array(quarterly)

    # Находим категории с нулевыми значениями
    zero_mask = (monthly == 0) | (quarterly == 0)

    if zero_mask.any():
        print(f"⚠️ Найдены нулевые значения в категориях:")
        for i, cat in enumerate(categories):
            if monthly[i] == 0:
                print(f"  - {cat}: monthly = 0")
            if quarterly[i] == 0:
                print(f"  - {cat}: quarterly = 0")

        # Вариант 1: Добавляем небольшое значение (0.5) к нулям
        monthly_adj = monthly.copy()
        quarterly_adj = quarterly.copy()

        for i in range(len(categories)):
            if monthly_adj[i] == 0:
                monthly_adj[i] = 0.5
            if quarterly_adj[i] == 0:
                quarterly_adj[i] = 0.5

        # Нормализуем сумму до 100
        monthly_adj = monthly_adj / monthly_adj.sum() * 100
        quarterly_adj = quarterly_adj / quarterly_adj.sum() * 100

        print("✅ Применена коррекция нулевых значений")
        return compare_distributions_core(monthly_adj, quarterly_adj, categories)
    else:
        return compare_distributions_core(monthly, quarterly, categories)


def compare_distributions_core(monthly, quarterly, categories):
    """
    Основная функция сравнения распределений
    """
    monthly = np.array(monthly)
    quarterly = np.array(quarterly)

    # Используем безопасную версию chi2_contingency
    chi2_stat, p_value, dof, expected = safe_chi2_contingency([monthly, quarterly])

    wasserstein_dist = wasserstein_distance(monthly, quarterly)
    mean_abs_diff = np.mean(np.abs(monthly - quarterly))
    max_diff = np.max(np.abs(monthly - quarterly))

    return {
        'chi2_stat': chi2_stat,
        'chi2_p_value': p_value,
        'wasserstein_dist': wasserstein_dist,
        'mean_abs_diff': mean_abs_diff,
        'max_diff': max_diff,
        'is_significant': p_value < 0.05 if not np.isnan(p_value) else False,
        'has_zero_categories': (monthly == 0).any() or (quarterly == 0).any()
    }