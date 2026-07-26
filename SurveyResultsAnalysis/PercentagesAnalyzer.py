import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import chi2_contingency, wasserstein_distance
from datetime import datetime

from SurveyResultsAnalysis.helpers import compare_distributions_robust
from SurveyResultsAnalysis.visualizationHelpers import align_quarterly_to_monthly_percentages, \
    plot_comparison_percentages, plot_diff_heatmap_percentages, plot_evolution_percentages


class PercentagesAnalyzer:
    """
    Класс для анализа агрегированных категориальных данных
    """

    def __init__(self, monthly_df, quarterly_df, categories):
        self.monthly_df = monthly_df
        self.quarterly_df = quarterly_df
        self.categories = categories

        # Выравниваем данные (добавляем нули для отсутствующих дат)
        self.aligned_df = align_quarterly_to_monthly_percentages(monthly_df, quarterly_df)

        # Результаты
        self.results = {}
        self._analyze_all_dates()

    def _analyze_all_dates(self):
        """Анализирует все даты"""
        for date in self.aligned_df.index:
            self.results[date] = self._compare_date(date)

    def _compare_date(self, date):
        """Сравнивает распределения для конкретной даты"""
        row = self.aligned_df.loc[date]
        monthly = [row[f'monthly_{cat}'] for cat in self.categories]
        quarterly = [row[f'quarterly_{cat}'] for cat in self.categories]

        # Проверяем, есть ли нулевые значения
        has_zeros = any(x == 0 for x in monthly) or any(x == 0 for x in quarterly)

        # Пытаемся выполнить хи-квадрат тест
        try:
            chi2_stat, p_value, dof, expected = chi2_contingency([monthly, quarterly])
        except ValueError:
            # Если ошибка, используем альтернативный подход
            chi2_stat = np.nan
            p_value = np.nan
            print(f"⚠️ Хи-квадрат тест не удался для {date}, использую альтернативные метрики")

        # Расстояние Вассерштейна (работает всегда)
        wasserstein_dist = wasserstein_distance(monthly, quarterly)

        # Средняя абсолютная разница
        mean_abs_diff = np.mean(np.abs(np.array(monthly) - np.array(quarterly)))

        # Максимальная разница
        max_diff = np.max(np.abs(np.array(monthly) - np.array(quarterly)))

        return {
            'date': date,
            'monthly': monthly,
            'quarterly': quarterly,
            'chi2_stat': chi2_stat,
            'chi2_p_value': p_value,
            'wasserstein_dist': wasserstein_dist,
            'mean_abs_diff': mean_abs_diff,
            'max_diff': max_diff,
            'is_significant': p_value < 0.05 if not np.isnan(p_value) else False,
            'has_zeros': has_zeros
        }

    def get_summary(self):
        """Возвращает сводку результатов"""
        dates = sorted(self.results.keys())
        return pd.DataFrame({
            'date': dates,
            'chi2_stat': [self.results[d]['chi2_stat'] for d in dates],
            'chi2_p_value': [self.results[d]['chi2_p_value'] for d in dates],
            'wasserstein_dist': [self.results[d]['wasserstein_dist'] for d in dates],
            'mean_abs_diff': [self.results[d]['mean_abs_diff'] for d in dates],
            'max_diff': [self.results[d]['max_diff'] for d in dates],
            'significant': [self.results[d]['is_significant'] for d in dates],
            'has_zeros': [self.results[d]['has_zeros'] for d in dates]
        })

    def get_dates_with_zeros(self):
        """Возвращает даты, где есть нулевые значения"""
        return [d for d in self.results if self.results[d]['has_zeros']]

    def plot_all(self, save_prefix='percentages_analysis'):
        """Создает все графики"""
        # 1. Эволюция
        plot_evolution_percentages(self.aligned_df, self.categories,
                                   save_path=f'{save_prefix}_evolution.png')

        # 2. Heatmap
        plot_diff_heatmap_percentages(self.aligned_df, self.categories,
                                      save_path=f'{save_prefix}_heatmap.png')

        # 3. Сравнение для первых 3 дат
        dates = self.aligned_df.index[:min(3, len(self.aligned_df))]
        for date in dates:
            plot_comparison_percentages(self.aligned_df, date, self.categories,
                                        save_path=f'{save_prefix}_comparison_{date.strftime("%Y%m")}.png')
