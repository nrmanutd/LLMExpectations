import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from scipy.stats import chi2_contingency, wasserstein_distance


def prepare_comparison_data(monthly_df, quarterly_agg_df):
    """
    Подготавливает данные для сравнения

    Args:
        monthly_df: DataFrame с месячными данными (index - даты)
        quarterly_agg_df: DataFrame с агрегированными квартальными данными (колонка 'date')

    Returns:
        DataFrame с выровненными данными
    """
    # Убеждаемся, что даты в квартальных данных - это datetime
    quarterly_agg_df['date'] = pd.to_datetime(quarterly_agg_df['date'])

    # Получаем квартальные даты для месяцев (берем первое число каждого квартала)
    quarterly_dates = quarterly_agg_df['date'].values

    # Выбираем из месячных данных только те даты, которые есть в квартальных
    monthly_quarterly = monthly_df.loc[quarterly_dates].copy()

    # Создаем DataFrame для сравнения
    comparison_df = pd.DataFrame({
        'date': quarterly_dates,
        'monthly_observable': monthly_quarterly['observable_inflation'].values,
        'monthly_expected': monthly_quarterly['expected_inflation'].values,
        'quarterly_observable_mean': quarterly_agg_df['obs_mean'].values,
        'quarterly_expected_mean': quarterly_agg_df['exp_mean'].values
    })

    return comparison_df


def calculate_statistics(x, y):
    """
    Рассчитывает статистики для сравнения двух рядов

    Args:
        x: первый ряд (например, фактические данные)
        y: второй ряд (например, смоделированные данные)

    Returns:
        dict со статистиками
    """
    # Очищаем от NaN
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) < 2:
        return {
            'r_squared': np.nan,
            'correlation': np.nan,
            'slope': np.nan,
            'intercept': np.nan,
            'p_value': np.nan,
            'std_err': np.nan,
            'n_obs': len(x_clean)
        }

    # Расчет корреляции Пирсона
    correlation, p_value = stats.pearsonr(x_clean, y_clean)

    # Линейная регрессия
    X = sm.add_constant(x_clean)
    model = sm.OLS(y_clean, X).fit()

    # R-squared
    r_squared = model.rsquared

    # Исправление: params теперь ndarray, используем индексы
    params = model.params
    if len(params) > 1:
        slope = params[1]  # вместо params.iloc[1]
        intercept = params[0]  # вместо params.iloc[0]
    else:
        slope = np.nan
        intercept = np.nan

    # Исправление для p-values
    pvalues = model.pvalues
    if len(pvalues) > 1:
        p_value_slope = pvalues[1]  # вместо pvalues.iloc[1]
    else:
        p_value_slope = np.nan

    # Исправление для standard errors
    bse = model.bse
    if len(bse) > 1:
        std_err = bse[1]  # вместо bse.iloc[1]
    else:
        std_err = np.nan

    # Количество наблюдений
    n_obs = len(x_clean)

    # Определяем значимость
    if not np.isnan(p_value_slope):
        if p_value_slope < 0.001:
            significance = '***'
        elif p_value_slope < 0.01:
            significance = '**'
        elif p_value_slope < 0.05:
            significance = '*'
        else:
            significance = 'n.s.'
    else:
        significance = 'n.s.'

    return {
        'r_squared': r_squared,
        'correlation': correlation,
        'slope': slope,
        'intercept': intercept,
        'p_value': p_value_slope,
        'std_err': std_err,
        'n_obs': n_obs,
        'significance': significance
    }

def plot_comparison(comparison_df, obs_stats, exp_stats, save_path=None):
    """
    Создает два графика для сравнения данных
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # ---- График 1: Observable Inflation ----
    ax1 = axes[0]

    # Данные
    ax1.scatter(comparison_df['quarterly_observable_mean'], comparison_df['monthly_observable'],
                alpha=0.7, s=50, color='#2E86AB', label='Наблюдения')

    # Линия x=y (идеальное совпадение)
    min_val = min(comparison_df['monthly_observable'].min(),
                  comparison_df['quarterly_observable_mean'].min())
    max_val = max(comparison_df['monthly_observable'].max(),
                  comparison_df['quarterly_observable_mean'].max())
    ax1.plot([min_val, max_val], [min_val, max_val],
             'k--', alpha=0.5, label='Идеальное совпадение (y=x)')

    # Линия регрессии
    x = comparison_df['quarterly_observable_mean'].values
    y = comparison_df['monthly_observable'].values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) > 1:
        X = sm.add_constant(x_clean)
        model = sm.OLS(y_clean, X).fit()
        x_line = np.linspace(x_clean.min(), x_clean.max(), 100)
        y_line = model.params[0] + model.params[1] * x_line
        ax1.plot(x_line, y_line, 'r-', linewidth=2,
                 label=f'Регрессия (R² = {obs_stats["r_squared"]:.3f})')

    # Настройка графика
    ax1.set_title('Observable Inflation: Monthly vs Quarterly',
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Модель (среднее по опросу)', fontsize=12)
    ax1.set_ylabel('Инфом факт (наблюдаемая инфляция)', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Добавляем статистику на график
    stats_text = f"""R² = {obs_stats['r_squared']:.3f}
Corr = {obs_stats['correlation']:.3f}
Slope = {obs_stats['slope']:.3f}{obs_stats['significance']}
n = {obs_stats['n_obs']}
p = {obs_stats['p_value']:.4f}"""

    ax1.text(0.05, 0.95, stats_text,
             transform=ax1.transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=10)

    # ---- График 2: Expected Inflation ----
    ax2 = axes[1]

    # Данные
    ax2.scatter(comparison_df['quarterly_expected_mean'], comparison_df['monthly_expected'],
                alpha=0.7, s=50, color='#A23B72', label='Наблюдения')

    # Линия x=y
    min_val = min(comparison_df['monthly_expected'].min(),
                  comparison_df['quarterly_expected_mean'].min())
    max_val = max(comparison_df['monthly_expected'].max(),
                  comparison_df['quarterly_expected_mean'].max())
    ax2.plot([min_val, max_val], [min_val, max_val],
             'k--', alpha=0.5, label='Идеальное совпадение (y=x)')

    # Линия регрессии
    x = comparison_df['quarterly_expected_mean'].values
    y = comparison_df['monthly_expected'].values
    mask = ~(np.isnan(x) | np.isnan(y))
    x_clean = x[mask]
    y_clean = y[mask]

    if len(x_clean) > 1:
        X = sm.add_constant(x_clean)
        model = sm.OLS(y_clean, X).fit()
        x_line = np.linspace(x_clean.min(), x_clean.max(), 100)
        y_line = model.params[0] + model.params[1] * x_line
        ax2.plot(x_line, y_line, 'r-', linewidth=2,
                 label=f'Регрессия (R² = {exp_stats["r_squared"]:.3f})')

    # Настройка графика
    ax2.set_title('Expected Inflation: Monthly vs Quarterly',
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Модель (средняя по опросу)', fontsize=12)
    ax2.set_ylabel('Инфом факт (ожидаемая инфляция)', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    # Добавляем статистику на график
    stats_text = f"""R² = {exp_stats['r_squared']:.3f}
Corr = {exp_stats['correlation']:.3f}
Slope = {exp_stats['slope']:.3f}{exp_stats['significance']}
n = {exp_stats['n_obs']}
p = {exp_stats['p_value']:.4f}"""

    ax2.text(0.05, 0.95, stats_text,
             transform=ax2.transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
             fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ График сохранен как: {save_path}")

    plt.show()

    return fig


def plot_time_series(comparison_df, save_path=None):
    """
    Визуализирует временные ряды для обоих показателей с доверительными интервалами (± std)
    """
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # Observable Inflation
    ax1 = axes[0]
    ax1.plot(comparison_df['date'], comparison_df['monthly_observable'],
             'o-', label='Инфом (фактические)', color='#2E86AB', markersize=8, linewidth=2)

    # График для quarterly с доверительным интервалом
    ax1.plot(comparison_df['date'], comparison_df['quarterly_observable_mean'],
             's-', label='Модель (среднее по опросу)', color='#E74C3C', markersize=8, linewidth=2)

    # Добавляем доверительный интервал (± std) для observable
    if 'quarterly_observable_std' in comparison_df.columns:
        ax1.fill_between(comparison_df['date'],
                         comparison_df['quarterly_observable_mean'] - comparison_df['quarterly_observable_std'],
                         comparison_df['quarterly_observable_mean'] + comparison_df['quarterly_observable_std'],
                         color='#E74C3C', alpha=0.2, label='±1 std')

    ax1.set_title('Наблюдаемая инфляция: сравнение рядов', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Дата', fontsize=12)
    ax1.set_ylabel('Инфляция, %', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # Expected Inflation
    ax2 = axes[1]
    ax2.plot(comparison_df['date'], comparison_df['monthly_expected'],
             'o-', label='Инфом (фактические)', color='#A23B72', markersize=8, linewidth=2)

    # График для quarterly с доверительным интервалом
    ax2.plot(comparison_df['date'], comparison_df['quarterly_expected_mean'],
             's-', label='Модель (среднее по опросу)', color='#F39C12', markersize=8, linewidth=2)

    # Добавляем доверительный интервал (± std) для expected
    if 'quarterly_expected_std' in comparison_df.columns:
        ax2.fill_between(comparison_df['date'],
                         comparison_df['quarterly_expected_mean'] - comparison_df['quarterly_expected_std'],
                         comparison_df['quarterly_expected_mean'] + comparison_df['quarterly_expected_std'],
                         color='#F39C12', alpha=0.2, label='±1 std')

    ax2.set_title('Ожидаемая инфляция: сравнение рядов', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Дата', fontsize=12)
    ax2.set_ylabel('Инфляция, %', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ График сохранен как: {save_path}")

    plt.show()


def plot_log_returns(comparison_df, save_path=None):
    """
    Визуализирует логарифмы приростов (log-returns) для обоих показателей с доверительными интервалами (± std)

    Parameters:
    -----------
    comparison_df : pandas.DataFrame
        DataFrame с колонками: date, monthly_observable, quarterly_observable_mean,
        quarterly_observable_std, monthly_expected, quarterly_expected_mean, quarterly_expected_std
    save_path : str, optional
        Путь для сохранения графика
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(14, 10))

    # ---- Observable Inflation ----
    ax1 = axes[0]

    # Вычисляем логарифмические приросты для observable
    monthly_obs = comparison_df['monthly_observable'].values
    quarterly_obs = comparison_df['quarterly_observable_mean'].values
    quarterly_std = comparison_df[
        'quarterly_observable_std'].values if 'quarterly_observable_std' in comparison_df.columns else None

    # Преобразуем в Series для diff()
    monthly_obs_series = pd.Series(monthly_obs)
    quarterly_obs_series = pd.Series(quarterly_obs)

    # Вычисляем log-returns (логарифмы приростов)
    monthly_log_returns = np.log(monthly_obs_series).diff().dropna()
    quarterly_log_returns = np.log(quarterly_obs_series).diff().dropna()

    # Даты для log-returns (пропускаем первую дату, т.к. diff удаляет первое значение)
    dates_log = comparison_df['date'].iloc[1:]

    # Выравниваем длины
    min_len = min(len(dates_log), len(monthly_log_returns), len(quarterly_log_returns))
    dates_log = dates_log.iloc[:min_len]
    monthly_log_returns = monthly_log_returns.iloc[:min_len]
    quarterly_log_returns = quarterly_log_returns.iloc[:min_len]

    # Рисуем log-returns
    ax1.plot(dates_log, monthly_log_returns,
             'o-', label='Monthly (фактические)', color='#2E86AB', markersize=8, linewidth=2)

    ax1.plot(dates_log, quarterly_log_returns,
             's-', label='Quarterly (среднее по опросу)', color='#E74C3C', markersize=8, linewidth=2)

    # Добавляем доверительный интервал для quarterly log-returns (если есть std)
    if quarterly_std is not None:
        # Для доверительного интервала log-returns используем приближение:
        # std(log(x)) ≈ std(x)/x для малых изменений
        # Но лучше использовать дельта-метод: var(log(x)) ≈ var(x)/x^2
        quarterly_mean = comparison_df['quarterly_observable_mean'].values
        quarterly_std_log = quarterly_std / quarterly_mean  # приблизительная std для log

        # Сдвигаем std, чтобы совпадало с log-returns (первое значение пропускаем)
        quarterly_std_log_shifted = quarterly_std_log[1:][:min_len]
        quarterly_log_returns_vals = quarterly_log_returns.values

        # Доверительный интервал для log-returns
        ax1.fill_between(dates_log,
                         quarterly_log_returns_vals - quarterly_std_log_shifted,
                         quarterly_log_returns_vals + quarterly_std_log_shifted,
                         color='#E74C3C', alpha=0.2, label='±1 std (log)')

    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_title('Observable Inflation: Логарифмы приростов (log-returns)',
                  fontsize=14, fontweight='bold')
    ax1.set_xlabel('Дата', fontsize=12)
    ax1.set_ylabel('log(инфляция(t) / инфляция(t-1))', fontsize=12)
    ax1.legend(loc='best', fontsize=10)
    ax1.grid(True, alpha=0.3)

    # ---- Expected Inflation ----
    ax2 = axes[1]

    # Вычисляем логарифмические приросты для expected
    monthly_exp = comparison_df['monthly_expected'].values
    quarterly_exp = comparison_df['quarterly_expected_mean'].values
    quarterly_exp_std = comparison_df[
        'quarterly_expected_std'].values if 'quarterly_expected_std' in comparison_df.columns else None

    # Преобразуем в Series для diff()
    monthly_exp_series = pd.Series(monthly_exp)
    quarterly_exp_series = pd.Series(quarterly_exp)

    # Вычисляем log-returns
    monthly_exp_log_returns = np.log(monthly_exp_series).diff().dropna()
    quarterly_exp_log_returns = np.log(quarterly_exp_series).diff().dropna()

    # Выравниваем длины
    min_len_exp = min(len(dates_log), len(monthly_exp_log_returns), len(quarterly_exp_log_returns))
    dates_log_exp = dates_log.iloc[:min_len_exp]
    monthly_exp_log_returns = monthly_exp_log_returns.iloc[:min_len_exp]
    quarterly_exp_log_returns = quarterly_exp_log_returns.iloc[:min_len_exp]

    # Рисуем log-returns
    ax2.plot(dates_log_exp, monthly_exp_log_returns,
             'o-', label='Monthly (фактические)', color='#A23B72', markersize=8, linewidth=2)

    ax2.plot(dates_log_exp, quarterly_exp_log_returns,
             's-', label='Quarterly (среднее по опросу)', color='#F39C12', markersize=8, linewidth=2)

    # Добавляем доверительный интервал для quarterly exp log-returns
    if quarterly_exp_std is not None:
        quarterly_exp_mean = comparison_df['quarterly_expected_mean'].values
        quarterly_exp_std_log = quarterly_exp_std / quarterly_exp_mean

        quarterly_exp_std_log_shifted = quarterly_exp_std_log[1:][:min_len_exp]
        quarterly_exp_log_returns_vals = quarterly_exp_log_returns.values

        ax2.fill_between(dates_log_exp,
                         quarterly_exp_log_returns_vals - quarterly_exp_std_log_shifted,
                         quarterly_exp_log_returns_vals + quarterly_exp_std_log_shifted,
                         color='#F39C12', alpha=0.2, label='±1 std (log)')

    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_title('Expected Inflation: Логарифмы приростов (log-returns)',
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Дата', fontsize=12)
    ax2.set_ylabel('log(инфляция(t) / инфляция(t-1))', fontsize=12)
    ax2.legend(loc='best', fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ График сохранен как: {save_path}")

    plt.show()

    return fig, axes


def detailed_analysis(comparison_df):
    """
    Проводит детальный анализ сравнения
    """
    # 1. Основные статистики по рядам
    print("=" * 80)
    print("ДЕТАЛЬНЫЙ АНАЛИЗ ДАННЫХ")
    print("=" * 80)

    # Статистики по месяцам
    print("\n📊 СТАТИСТИКИ МЕСЯЧНЫХ ДАННЫХ:")
    monthly_stats = pd.DataFrame({
        'Observable': comparison_df['monthly_observable'].describe(),
        'Expected': comparison_df['monthly_expected'].describe()
    })
    print(monthly_stats)

    # Статистики по квартальным данным
    print("\n📊 СТАТИСТИКИ КВАРТАЛЬНЫХ ДАННЫХ:")
    quarterly_stats = pd.DataFrame({
        'Observable': comparison_df['quarterly_observable_mean'].describe(),
        'Expected': comparison_df['quarterly_expected_mean'].describe()
    })
    print(quarterly_stats)

    # 2. Разницы между рядами
    print("\n📊 РАЗНИЦЫ МЕЖДУ РЯДАМИ:")
    diff_obs = comparison_df['monthly_observable'] - comparison_df['quarterly_observable_mean']
    diff_exp = comparison_df['monthly_expected'] - comparison_df['quarterly_expected_mean']

    diff_stats = pd.DataFrame({
        'Observable Diff': diff_obs.describe(),
        'Expected Diff': diff_exp.describe()
    })
    print(diff_stats)

    # 3. Корреляции
    print("\n📊 КОРРЕЛЯЦИИ:")
    corr_matrix = comparison_df[['monthly_observable', 'quarterly_observable_mean',
                                 'monthly_expected', 'quarterly_expected_mean']].corr()
    print(corr_matrix)

    # 4. Коэффициенты регрессии
    print("\n📊 РЕГРЕССИОННЫЙ АНАЛИЗ:")

    # Observable
    X_obs = sm.add_constant(comparison_df['quarterly_observable_mean'])
    y_obs = comparison_df['monthly_observable']
    model_obs = sm.OLS(y_obs, X_obs).fit()

    print("\nObservable Inflation:")
    print(f"  R² = {model_obs.rsquared:.4f}")
    print(f"  Adj R² = {model_obs.rsquared_adj:.4f}")
    print(f"  Coef: {model_obs.params[1]:.4f} (p={model_obs.pvalues[1]:.4f})")
    print(f"  Intercept: {model_obs.params[0]:.4f} (p={model_obs.pvalues[0]:.4f})")
    print(f"  Std Error: {model_obs.bse[1]:.4f}")
    print(f"  F-statistic: {model_obs.fvalue:.4f} (p={model_obs.f_pvalue:.4f})")

    # Expected
    X_exp = sm.add_constant(comparison_df['quarterly_expected_mean'])
    y_exp = comparison_df['monthly_expected']
    model_exp = sm.OLS(y_exp, X_exp).fit()

    print("\nExpected Inflation:")
    print(f"  R² = {model_exp.rsquared:.4f}")
    print(f"  Adj R² = {model_exp.rsquared_adj:.4f}")
    print(f"  Coef: {model_exp.params[1]:.4f} (p={model_exp.pvalues[1]:.4f})")
    print(f"  Intercept: {model_exp.params[0]:.4f} (p={model_exp.pvalues[0]:.4f})")
    print(f"  Std Error: {model_exp.bse[1]:.4f}")
    print(f"  F-statistic: {model_exp.fvalue:.4f} (p={model_exp.f_pvalue:.4f})")

    # 5. Диагностика остатков
    print("\n📊 ДИАГНОСТИКА ОСТАТКОВ:")

    # Observable
    residuals_obs = model_obs.resid
    print("\nObservable Inflation остатки:")
    print(f"  Mean: {residuals_obs.mean():.4f}")
    print(f"  Std: {residuals_obs.std():.4f}")
    print(f"  Min: {residuals_obs.min():.4f}")
    print(f"  Max: {residuals_obs.max():.4f}")

    # Expected
    residuals_exp = model_exp.resid
    print("\nExpected Inflation остатки:")
    print(f"  Mean: {residuals_exp.mean():.4f}")
    print(f"  Std: {residuals_exp.std():.4f}")
    print(f"  Min: {residuals_exp.min():.4f}")
    print(f"  Max: {residuals_exp.max():.4f}")

    return {
        'monthly_stats': monthly_stats,
        'quarterly_stats': quarterly_stats,
        'diff_stats': diff_stats,
        'corr_matrix': corr_matrix,
        'model_obs': model_obs,
        'model_exp': model_exp
    }


def align_quarterly_to_monthly_percentages(monthly_df, quarterly_df):
    """
    Выравнивает квартальные данные к месячным датам.
    Отсутствующие даты заполняются нулями.

    Args:
        monthly_df: DataFrame с месячными данными (индекс - даты)
        quarterly_df: DataFrame с квартальными данными (индекс - даты)

    Returns:
        DataFrame с выровненными данными
    """
    # Копируем данные
    monthly_aligned = monthly_df.copy()
    quarterly_aligned = quarterly_df.copy()

    # Убеждаемся, что индексы в datetime
    if not pd.api.types.is_datetime64_any_dtype(monthly_aligned.index):
        monthly_aligned.index = pd.to_datetime(monthly_aligned.index)

    if not pd.api.types.is_datetime64_any_dtype(quarterly_aligned.index):
        quarterly_aligned.index = pd.to_datetime(quarterly_aligned.index)

    # Получаем все даты из квартальных данных
    quarterly_dates = quarterly_aligned.index

    # Для каждой квартальной даты проверяем, есть ли она в monthly
    for q_date in quarterly_dates:
        if q_date not in monthly_aligned.index:
            # Добавляем строку с нулями
            zero_row = pd.Series(0, index=monthly_aligned.columns, name=q_date)
            monthly_aligned = pd.concat([monthly_aligned, zero_row.to_frame().T])

    # Сортируем по дате
    monthly_aligned.sort_index(inplace=True)

    # Создаем aligned_df с колонками monthly_* и quarterly_*
    aligned_data = []

    for date in monthly_aligned.index:
        # Месячные данные (или нули, если дата добавлена)
        monthly_row = monthly_aligned.loc[date]

        # Квартальные данные (ищем ближайший квартал)
        if date in quarterly_aligned.index:
            quarterly_row = quarterly_aligned.loc[date]
        else:
            # Ищем ближайший квартал
            quarterly_dates = quarterly_aligned.index
            nearest_idx = quarterly_dates.get_indexer([date], method='nearest')[0]
            if nearest_idx != -1:
                nearest_date = quarterly_dates[nearest_idx]
                quarterly_row = quarterly_aligned.loc[nearest_date]
            else:
                quarterly_row = pd.Series(0, index=quarterly_aligned.columns)

        # Собираем строку
        row = {'date': date}
        for col in monthly_aligned.columns:
            row[f'monthly_{col}'] = monthly_row[col]
            row[f'quarterly_{col}'] = quarterly_row.get(col, 0)

        aligned_data.append(row)

    aligned_df = pd.DataFrame(aligned_data).set_index('date')

    # Добавляем информацию о добавленных датах
    original_monthly_dates = set(monthly_df.index)
    added_dates = set(aligned_df.index) - original_monthly_dates

    if added_dates:
        print(f"⚠️ Добавлено {len(added_dates)} дат с нулевыми значениями:")
        for date in sorted(added_dates)[:5]:
            print(f"  - {date.strftime('%Y-%m-%d')}")
        if len(added_dates) > 5:
            print(f"  ... и еще {len(added_dates) - 5} дат")

    return aligned_df


def compare_distributions_for_date(aligned_df, date, categories):
    """
    Сравнивает распределения для конкретной даты

    Args:
        aligned_df: DataFrame с выровненными данными
        date: дата для сравнения
        categories: список категорий

    Returns:
        dict с результатами сравнения
    """
    row = aligned_df.loc[date]

    monthly = [row[f'monthly_{cat}'] for cat in categories]
    quarterly = [row[f'quarterly_{cat}'] for cat in categories]

    # Статистические тесты
    chi2_stat, p_value, dof, expected = chi2_contingency([monthly, quarterly])
    wasserstein_dist = wasserstein_distance(monthly, quarterly)
    mean_abs_diff = np.mean(np.abs(np.array(monthly) - np.array(quarterly)))
    max_diff = np.max(np.abs(np.array(monthly) - np.array(quarterly)))

    # Детали по категориям
    category_diff = {}
    for i, cat in enumerate(categories):
        category_diff[cat] = {
            'monthly': monthly[i],
            'quarterly': quarterly[i],
            'diff': monthly[i] - quarterly[i]
        }

    return {
        'date': date,
        'monthly': monthly,
        'quarterly': quarterly,
        'categories': categories,
        'chi2_stat': chi2_stat,
        'chi2_p_value': p_value,
        'wasserstein_dist': wasserstein_dist,
        'mean_abs_diff': mean_abs_diff,
        'max_diff': max_diff,
        'is_significant': p_value < 0.05,
        'category_diff': category_diff
    }


def plot_comparison_percentages(aligned_df, date, categories, save_path=None):
    """
    Создает график сравнения для конкретной даты
    """
    row = aligned_df.loc[date]
    monthly = [row[f'monthly_{cat}'] for cat in categories]
    quarterly = [row[f'quarterly_{cat}'] for cat in categories]

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))

    # 1. Сравнение распределений
    ax1 = axes[0]
    x = np.arange(len(categories))
    width = 0.35

    bars1 = ax1.bar(x - width / 2, monthly, width, label='Месячные (факт)',
                    color='#2E86AB', alpha=0.8)
    bars2 = ax1.bar(x + width / 2, quarterly, width, label='Квартальные (модель)',
                    color='#A23B72', alpha=0.8)

    # Добавляем значения
    for i, (m, q) in enumerate(zip(monthly, quarterly)):
        ax1.text(i - width / 2, m + 0.5, f'{m:.0f}%',
                 ha='center', va='bottom', fontsize=8)
        ax1.text(i + width / 2, q + 0.5, f'{q:.0f}%',
                 ha='center', va='bottom', fontsize=8)

    ax1.set_xlabel('Категории', fontsize=12)
    ax1.set_ylabel('Доля, %', fontsize=12)
    ax1.set_title(f'Сравнение распределений\n{date.strftime("%Y-%m")}',
                  fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=45, ha='right')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, axis='y')

    # 2. Разница
    ax2 = axes[1]
    diff = np.array(monthly) - np.array(quarterly)
    colors = ['green' if d > 0 else 'red' if d < 0 else 'gray' for d in diff]

    bars = ax2.bar(x, diff, color=colors, alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    for i, d in enumerate(diff):
        ax2.text(i, d + (0.5 if d >= 0 else -1.5),
                 f'{d:.1f}%', ha='center', fontsize=9)

    ax2.set_xlabel('Категории', fontsize=12)
    ax2.set_ylabel('Разница (факт - модель), %', fontsize=12)
    ax2.set_title('Разница между распределениями', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')

    # Статистика
    chi2_stat, p_value, dof, expected = chi2_contingency([monthly, quarterly])
    stats_text = f"Хи-квадрат: {chi2_stat:.2f}\np-value: {p_value:.4f}"
    ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
             fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()

    return fig


def plot_evolution_percentages(aligned_df, categories, save_path=None):
    """
    Показывает эволюцию распределений по времени
    """
    fig, axes = plt.subplots(2, 1, figsize=(16, 12))

    # 1. Месячные данные
    ax1 = axes[0]
    for cat in categories:
        ax1.plot(aligned_df.index, aligned_df[f'monthly_{cat}'],
                 marker='o', label=cat, linewidth=2, markersize=4)

    ax1.set_title('Месячные данные (фактические)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Дата', fontsize=12)
    ax1.set_ylabel('Доля, %', fontsize=12)
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    ax1.grid(True, alpha=0.3)

    # 2. Квартальные данные (выровненные)
    ax2 = axes[1]
    for cat in categories:
        ax2.plot(aligned_df.index, aligned_df[f'quarterly_{cat}'],
                 marker='s', label=cat, linewidth=2, markersize=4, linestyle='--')

    ax2.set_title('Квартальные данные (моделируемые, выровненные)',
                  fontsize=14, fontweight='bold')
    ax2.set_xlabel('Дата', fontsize=12)
    ax2.set_ylabel('Доля, %', fontsize=12)
    ax2.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()

    return fig


def plot_diff_heatmap_percentages(aligned_df, categories, save_path=None):
    """
    Создает heatmap разниц между распределениями
    """
    dates = aligned_df.index
    diff_matrix = np.zeros((len(dates), len(categories)))

    for i, date in enumerate(dates):
        for j, cat in enumerate(categories):
            diff_matrix[i, j] = aligned_df.loc[date, f'monthly_{cat}'] - \
                                aligned_df.loc[date, f'quarterly_{cat}']

    fig, ax = plt.subplots(figsize=(14, len(dates) * 0.3 + 2))

    # Рисуем heatmap
    im = ax.imshow(diff_matrix, cmap='RdBu_r', aspect='auto', vmin=-20, vmax=20)

    # Настройка осей
    ax.set_xticks(np.arange(len(categories)))
    ax.set_yticks(np.arange(len(dates)))
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.set_yticklabels([d.strftime('%Y-%m') for d in dates])

    # Добавляем значения
    for i in range(len(dates)):
        for j in range(len(categories)):
            text = ax.text(j, i, f'{diff_matrix[i, j]:.1f}',
                           ha="center", va="center",
                           color="white" if abs(diff_matrix[i, j]) > 10 else "black",
                           fontsize=8)

    ax.set_title('Heatmap разниц (факт - модель), %',
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Категории', fontsize=12)
    ax.set_ylabel('Дата', fontsize=12)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Разница, %', fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    plt.show()

    return fig
