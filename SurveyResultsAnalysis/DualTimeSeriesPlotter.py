import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Union, List, Optional, Tuple


class DualTimeSeriesPlotter:
    """
    Класс для визуализации двух временных рядов с разными датами
    """

    def __init__(self,
                 data1: Union[pd.Series, pd.DataFrame],
                 data2: Union[pd.Series, pd.DataFrame],
                 name1: str = "Series 1",
                 name2: str = "Series 2"):
        """
        Инициализация с двумя наборами данных

        Args:
            data1: первый временной ряд (индекс - даты, значения - данные)
            data2: второй временной ряд (индекс - даты, значения - данные)
            name1: название первого ряда для легенды
            name2: название второго ряда для легенды
        """
        self.data1 = self._ensure_series(data1)
        self.data2 = self._ensure_series(data2)
        self.name1 = name1
        self.name2 = name2

        # Приводим индексы к datetime
        self.data1.index = pd.to_datetime(self.data1.index)
        self.data2.index = pd.to_datetime(self.data2.index)

        # Сортируем по датам
        self.data1 = self.data1.sort_index()
        self.data2 = self.data2.sort_index()

    def _ensure_series(self, data) -> pd.Series:
        """Преобразует данные в pandas Series если нужно"""
        if isinstance(data, pd.Series):
            return data.copy()
        elif isinstance(data, pd.DataFrame):
            # Берем первый столбец если их несколько
            return data.iloc[:, 0].copy()
        elif isinstance(data, (list, np.ndarray)):
            # Если список, создаем индекс по умолчанию
            return pd.Series(data)
        else:
            raise ValueError(f"Неподдерживаемый тип данных: {type(data)}")

    def plot(self,
             figsize: Tuple[int, int] = (12, 6),
             title: str = "Time Series Comparison",
             xlabel: str = "Date",
             ylabel: str = "Value",
             style1: str = 'o-',
             style2: str = 's-',
             color1: str = 'blue',
             color2: str = 'red',
             alpha1: float = 0.7,
             alpha2: float = 0.7,
             markersize: int = 6,
             linewidth: int = 2,
             grid: bool = True,
             legend_loc: str = 'best',
             save_path: Optional[str] = None,
             show: bool = True):
        """
        Создает график двух временных рядов

        Args:
            figsize: размер фигуры
            title: заголовок
            xlabel: подпись оси X
            ylabel: подпись оси Y
            style1: стиль для первого ряда
            style2: стиль для второго ряда
            color1: цвет для первого ряда
            color2: цвет для второго ряда
            alpha1: прозрачность для первого ряда
            alpha2: прозрачность для второго ряда
            markersize: размер маркеров
            linewidth: толщина линии
            grid: показывать сетку
            legend_loc: позиция легенды
            save_path: путь для сохранения графика
            show: показывать график
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Рисуем первый ряд
        ax.plot(self.data1.index, self.data1.values,
                style1, label=self.name1,
                color=color1, alpha=alpha1,
                markersize=markersize, linewidth=linewidth)

        # Рисуем второй ряд
        ax.plot(self.data2.index, self.data2.values,
                style2, label=self.name2,
                color=color2, alpha=alpha2,
                markersize=markersize, linewidth=linewidth)

        # Настройки графика
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3)

        ax.legend(loc=legend_loc)

        # Форматируем даты на оси X
        fig.autofmt_xdate()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ График сохранен: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return fig, ax

    def plot_time_series(save_path=None):
        """
        Визуализирует временные ряды для обоих показателей с доверительными интервалами (± std)
        """
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))

        # Observable Inflation
        ax1 = axes[0]
        ax1.plot(self. comparison_df['date'], comparison_df['monthly_observable'],
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


    def plot_with_ci(self,
                     ci_data1: Optional[Tuple[pd.Series, pd.Series]] = None,
                     ci_data2: Optional[Tuple[pd.Series, pd.Series]] = None,
                     figsize: Tuple[int, int] = (12, 6),
                     title: str = "Time Series with Confidence Intervals",
                     xlabel: str = "Date",
                     ylabel: str = "Value",
                     color1: str = 'blue',
                     color2: str = 'red',
                     alpha: float = 0.3,
                     save_path: Optional[str] = None,
                     show: bool = True):
        """
        Создает график с доверительными интервалами

        Args:
            ci_data1: (lower_bound, upper_bound) для первого ряда
            ci_data2: (lower_bound, upper_bound) для второго ряда
            другие параметры аналогичны plot()
        """
        fig, ax = plt.subplots(figsize=figsize)

        # Первый ряд с CI
        ax.plot(self.data1.index, self.data1.values,
                'o-', label=self.name1, color=color1,
                markersize=5, linewidth=2)

        if ci_data1:
            lower1, upper1 = ci_data1
            ax.fill_between(self.data1.index, lower1, upper1,
                            alpha=alpha, color=color1, label=f'{self.name1} CI')

        # Второй ряд с CI
        ax.plot(self.data2.index, self.data2.values,
                's-', label=self.name2, color=color2,
                markersize=5, linewidth=2)

        if ci_data2:
            lower2, upper2 = ci_data2
            ax.fill_between(self.data2.index, lower2, upper2,
                            alpha=alpha, color=color2, label=f'{self.name2} CI')

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')

        fig.autofmt_xdate()
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✅ График сохранен: {save_path}")

        if show:
            plt.show()
        else:
            plt.close()

        return fig, ax

    def get_stats(self) -> pd.DataFrame:
        """Выводит статистику по данным"""
        stats = []
        for name, data in [('Series 1', self.data1), ('Series 2', self.data2)]:
            stats.append({
                'Series': name,
                'Count': len(data),
                'Min': data.min(),
                'Max': data.max(),
                'Mean': data.mean(),
                'Std': data.std(),
                'Start Date': data.index.min(),
                'End Date': data.index.max()
            })
        return pd.DataFrame(stats)


# Функция-помощник для создания графика из ваших данных
def plot_two_series(direct_estimations: pd.Series,
                    surveys: pd.Series,
                    title: str = "Direct Estimations vs Surveys",
                    ylabel: str = "Inflation",
                    save_path: Optional[str] = None):
    """
    Упрощенная функция для построения графиков directEstimations vs surveys
    """
    plotter = DualTimeSeriesPlotter(
        data1=direct_estimations,
        data2=surveys,
        name1="Direct Estimations",
        name2="Surveys"
    )

    # Выводим статистику
    print(plotter.get_stats())

    # Строим график
    plotter.plot(
        title=title,
        ylabel=ylabel,
        color1='#2E86C1',  # Синий
        color2='#E74C3C',  # Красный
        style1='o-',
        style2='s-',
        save_path=save_path
    )

    return plotter


# Пример использования с вашими данными
if __name__ == "__main__":
    # Пример данных с разными датами
    dates1 = pd.date_range('2022-01-01', '2022-12-31', freq='MS')  # Ежемесячно
    dates2 = pd.date_range('2022-01-15', '2022-12-15', freq='2MS')  # Каждые 2 месяца

    direct_est = pd.Series(np.random.randn(len(dates1)) * 0.5 + 2, index=dates1)
    surveys = pd.Series(np.random.randn(len(dates2)) * 0.3 + 1.8, index=dates2)

    # Простое использование
    plot_two_series(direct_est, surveys)

    # Более детальное использование
    plotter = DualTimeSeriesPlotter(
        data1=direct_est,
        data2=surveys,
        name1="Direct Estimations",
        name2="Survey Data"
    )

    # Вывод статистики
    print("\nСтатистика данных:")
    print(plotter.get_stats())

    # Построение графика с кастомными параметрами
    plotter.plot(
        title="Comparison: Direct Estimations vs Surveys",
        ylabel="Inflation Rate (%)",
        color1='darkblue',
        color2='darkred',
        style1='^-',
        style2='v-',
        markersize=8,
        linewidth=2.5,
        grid=True
    )