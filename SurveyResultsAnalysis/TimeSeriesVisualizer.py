import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Union


class TimeSeriesVisualizer:
    """
    Класс для визуализации временных рядов с несинхронизированными датами
    """

    def __init__(self,
                 direct_estimations: pd.DataFrame,
                 surveys: pd.DataFrame):
        """
        Args:
            direct_estimations: DataFrame с колонками 'observable_inflation', 'expected_inflation'
                               Индекс - даты
            surveys: DataFrame с колонками 'obs_mean', 'exp_mean'
                     Колонка 'date' - даты
        """
        self.direct_estimations = direct_estimations.copy()
        self.surveys = surveys.copy()

        # Приводим даты к datetime
        if not pd.api.types.is_datetime64_any_dtype(self.direct_estimations.index):
            self.direct_estimations.index = pd.to_datetime(self.direct_estimations.index)

        if not pd.api.types.is_datetime64_any_dtype(self.surveys['date']):
            self.surveys['date'] = pd.to_datetime(self.surveys['date'])

        # Сортируем
        self.direct_estimations = self.direct_estimations.sort_index()
        self.surveys = self.surveys.sort_values('date')

    def plot_timeseries(self,
                        variable: str = 'observable',  # или 'expected'
                        figsize: Tuple[int, int] = (14, 7),
                        title: Optional[str] = None,
                        xlabel: str = 'Date',
                        ylabel: str = 'Inflation',
                        color_direct: str = '#2E86C1',
                        color_survey: str = '#E74C3C',
                        marker_direct: str = 'o',
                        marker_survey: str = 's',
                        linestyle_direct: str = '-',
                        linestyle_survey: str = '-',
                        markersize: int = 6,
                        linewidth: int = 2,
                        alpha: float = 0.7,
                        show_ci: bool = True,
                        ci_alpha: float = 0.2,
                        grid: bool = True,
                        legend_loc: str = 'best',
                        save_path: Optional[str] = None,
                        show: bool = True):
        """
        Строит график временных рядов для observable или expected инфляции

        Args:
            variable: 'observable' или 'expected'
            figsize: размер фигуры
            title: заголовок
            xlabel: подпись оси X
            ylabel: подпись оси Y
            color_direct: цвет для direct estimations
            color_survey: цвет для surveys
            marker_direct: маркер для direct estimations
            marker_survey: маркер для surveys
            linestyle_direct: стиль линии для direct estimations
            linestyle_survey: стиль линии для surveys
            markersize: размер маркеров
            linewidth: толщина линии
            alpha: прозрачность
            show_ci: показывать доверительные интервалы для surveys
            ci_alpha: прозрачность доверительных интервалов
            grid: показывать сетку
            legend_loc: позиция легенды
            save_path: путь для сохранения
            show: показывать график
        """
        # Проверяем наличие данных
        if variable == 'observable':
            direct_col = 'observable_inflation'
            survey_col = 'obs_mean'
            survey_std_col = 'obs_std'
            default_title = 'Observable Inflation: Direct Estimations vs Surveys'
        else:  # 'expected'
            direct_col = 'expected_inflation'
            survey_col = 'exp_mean'
            survey_std_col = 'exp_std'
            default_title = 'Expected Inflation: Direct Estimations vs Surveys'

        if title is None:
            title = default_title

        # Проверяем наличие колонок
        if direct_col not in self.direct_estimations.columns:
            raise ValueError(f"Колонка '{direct_col}' не найдена в direct_estimations")

        if survey_col not in self.surveys.columns:
            raise ValueError(f"Колонка '{survey_col}' не найдена в surveys")

        # Создаем график
        fig, ax = plt.subplots(figsize=figsize)

        # Direct estimations
        ax.plot(self.direct_estimations.index,
                self.direct_estimations[direct_col],
                marker=marker_direct,
                linestyle=linestyle_direct,
                color=color_direct,
                linewidth=linewidth,
                markersize=markersize,
                alpha=alpha,
                label='Direct Estimations')

        # Surveys
        ax.plot(self.surveys['date'],
                self.surveys[survey_col],
                marker=marker_survey,
                linestyle=linestyle_survey,
                color=color_survey,
                linewidth=linewidth,
                markersize=markersize,
                alpha=alpha,
                label='Surveys (Quarterly)')

        # Доверительные интервалы для surveys
        if show_ci and survey_std_col in self.surveys.columns:
            ax.fill_between(self.surveys['date'],
                            self.surveys[survey_col] - self.surveys[survey_std_col],
                            self.surveys[survey_col] + self.surveys[survey_std_col],
                            alpha=ci_alpha,
                            color=color_survey,
                            label='Survey CI')

        # Настройки графика
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3)

        ax.legend(loc=legend_loc)

        # Форматируем даты
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

    def plot_both(self,
                  figsize: Tuple[int, int] = (14, 10),
                  save_prefix: Optional[str] = None,
                  **kwargs):
        """
        Строит два графика: для observable и expected инфляции

        Args:
            figsize: размер фигуры (будет разделен на 2 подграфика)
            save_prefix: префикс для сохранения (если None - не сохранять)
            **kwargs: дополнительные параметры для plot_timeseries
        """
        fig, axes = plt.subplots(2, 1, figsize=figsize)

        # Observable
        self._plot_on_axes(axes[0], 'observable', **kwargs)

        # Expected
        self._plot_on_axes(axes[1], 'expected', **kwargs)

        plt.tight_layout()

        if save_prefix:
            plt.savefig(f'{save_prefix}_both.png', dpi=300, bbox_inches='tight')
            print(f"✅ График сохранен: {save_prefix}_both.png")

        plt.show()
        return fig, axes

    def _plot_on_axes(self, ax, variable, **kwargs):
        """Вспомогательный метод для рисования на переданной оси"""
        # Определяем названия колонок
        if variable == 'observable':
            direct_col = 'observable_inflation'
            survey_col = 'obs_mean'
            survey_std_col = 'obs_std'
            title = 'Observable Inflation'
        else:
            direct_col = 'expected_inflation'
            survey_col = 'exp_mean'
            survey_std_col = 'exp_std'
            title = 'Expected Inflation'

        # Параметры по умолчанию
        color_direct = kwargs.get('color_direct', '#2E86C1')
        color_survey = kwargs.get('color_survey', '#E74C3C')
        marker_direct = kwargs.get('marker_direct', 'o')
        marker_survey = kwargs.get('marker_survey', 's')
        show_ci = kwargs.get('show_ci', True)
        ci_alpha = kwargs.get('ci_alpha', 0.2)
        alpha = kwargs.get('alpha', 0.7)
        grid = kwargs.get('grid', True)
        legend_loc = kwargs.get('legend_loc', 'best')

        # Direct estimations
        ax.plot(self.direct_estimations.index,
                self.direct_estimations[direct_col],
                marker=marker_direct,
                linestyle='-',
                color=color_direct,
                linewidth=2,
                markersize=6,
                alpha=alpha,
                label='Direct Estimations')

        # Surveys
        ax.plot(self.surveys['date'],
                self.surveys[survey_col],
                marker=marker_survey,
                linestyle='-',
                color=color_survey,
                linewidth=2,
                markersize=6,
                alpha=alpha,
                label='Surveys (Quarterly)')

        # Доверительные интервалы
        if show_ci and survey_std_col in self.surveys.columns:
            ax.fill_between(self.surveys['date'],
                            self.surveys[survey_col] - self.surveys[survey_std_col],
                            self.surveys[survey_col] + self.surveys[survey_std_col],
                            alpha=ci_alpha,
                            color=color_survey,
                            label='Survey CI')

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Inflation', fontsize=10)

        if grid:
            ax.grid(True, alpha=0.3)

        ax.legend(loc=legend_loc)

        # Исправлено: используем mdates.DateFormatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

        # Автоматически поворачиваем подписи дат
        fig = ax.get_figure()
        fig.autofmt_xdate()