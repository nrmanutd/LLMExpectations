from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Union
from datetime import datetime


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

    def _get_date_range(self,
                        start_date: Optional[Union[str, datetime]] = None,
                        end_date: Optional[Union[str, datetime]] = None,
                        use_intersection: bool = False) -> Tuple[datetime, datetime]:
        """
        Определяет диапазон дат для отображения.
        Более широкий ряд расширяется на одну свою точку с каждой стороны
        относительно более узкого ряда.

        Args:
            start_date: начальная дата (опционально)
            end_date: конечная дата (опционально)
            use_intersection: если True, использует пересечение диапазонов

        Returns:
            (start, end) кортеж с датами
        """
        # Получаем даты из данных
        direct_dates = self.direct_estimations.index
        survey_dates = self.surveys['date']

        # Проверяем, что данные не пустые
        if len(direct_dates) == 0 or len(survey_dates) == 0:
            print("⚠️ Один из рядов данных пуст")
            if len(direct_dates) > 0:
                return direct_dates.min(), direct_dates.max()
            elif len(survey_dates) > 0:
                return survey_dates.min(), survey_dates.max()
            else:
                return datetime.now(), datetime.now()

        direct_min = direct_dates.min()
        direct_max = direct_dates.max()
        survey_min = survey_dates.min()
        survey_max = survey_dates.max()

        if use_intersection:
            # Используем пересечение диапазонов
            raw_start = max(direct_min, survey_min)
            raw_end = min(direct_max, survey_max)

            # Проверяем, есть ли пересечение
            if raw_start > raw_end:
                print("⚠️ Ряды данных не пересекаются во времени")
                mid_point = direct_min + (direct_max - direct_min) / 2
                return mid_point - pd.Timedelta(days=30), mid_point + pd.Timedelta(days=30)

            # Определяем, какой ряд шире
            direct_range = (direct_max - direct_min).days
            survey_range = (survey_max - survey_min).days

            if direct_range > survey_range:
                # Direct шире - расширяем его на одну точку с каждой стороны
                left_dates = direct_dates[direct_dates < survey_min]
                if len(left_dates) > 0:
                    start = left_dates[-1]
                else:
                    start = survey_min

                right_dates = direct_dates[direct_dates > survey_max]
                if len(right_dates) > 0:
                    end = right_dates[0]
                else:
                    end = survey_max

            else:
                # Survey шире - расширяем его на одну точку с каждой стороны
                left_dates = survey_dates[survey_dates < direct_min]
                if len(left_dates) > 0:
                    start = left_dates.iloc[-1]
                else:
                    start = direct_min

                right_dates = survey_dates[survey_dates > direct_max]
                if len(right_dates) > 0:
                    end = right_dates.iloc[0]
                else:
                    end = direct_max

        else:
            # Используем объединение диапазонов
            direct_range = (direct_max - direct_min).days
            survey_range = (survey_max - survey_min).days

            if direct_range > survey_range:
                # Direct шире - расширяем его на одну точку с каждой стороны
                left_dates = direct_dates[direct_dates < survey_min]
                if len(left_dates) > 0:
                    start = left_dates[-1]
                else:
                    start = survey_min

                right_dates = direct_dates[direct_dates > survey_max]
                if len(right_dates) > 0:
                    end = right_dates[0]
                else:
                    end = survey_max

                start = max(start, direct_min)
                end = min(end, direct_max)

            elif survey_range > direct_range:
                # Survey шире - расширяем его на одну точку с каждой стороны
                left_dates = survey_dates[survey_dates < direct_min]
                if len(left_dates) > 0:
                    start = left_dates.iloc[-1]
                else:
                    start = direct_min

                right_dates = survey_dates[survey_dates > direct_max]
                if len(right_dates) > 0:
                    end = right_dates.iloc[0]
                else:
                    end = direct_max

                start = max(start, survey_min)
                end = min(end, survey_max)

            else:
                # Ряды одинаковой длины - берем объединение
                start = min(direct_min, survey_min)
                end = max(direct_max, survey_max)

        # Применяем пользовательские ограничения
        if start_date is not None:
            start_date = pd.to_datetime(start_date)
            start = max(start, start_date)

        if end_date is not None:
            end_date = pd.to_datetime(end_date)
            end = min(end, end_date)

        # Убеждаемся, что start <= end
        if start > end:
            print(f"⚠️ Начальная дата ({start}) позже конечной ({end}). Меняем местами.")
            start, end = end, start

        return start, end

    def _determine_date_format(self, start_date: datetime, end_date: datetime) -> str:
        """
        Определяет формат отображения дат в зависимости от длины периода
        """
        date_range = (end_date - start_date).days

        if date_range <= 60:  # до 2 месяцев
            return '%Y-%m-%d'
        elif date_range <= 365:  # до года
            return '%Y-%m-%d'
        elif date_range <= 1825:  # до 5 лет
            return '%Y-%m-%d'
        elif date_range <= 3650:  # до 10 лет
            return '%Y-%m-%d'
        else:  # более 10 лет
            return '%Y-%m-%d'

    def _determine_tick_interval(self, start_date: datetime, end_date: datetime) -> int:
        """
        Определяет интервал между метками на оси X
        """
        date_range = (end_date - start_date).days

        if date_range <= 60:  # до 2 месяцев
            return 3  # каждые 3 дня
        elif date_range <= 180:  # до полугода
            return 7  # каждую неделю
        elif date_range <= 365:  # до года
            return 14  # каждые 2 недели
        elif date_range <= 730:  # до 2 лет
            return 30  # ежемесячно
        elif date_range <= 1825:  # до 5 лет
            return 60  # каждые 2 месяца
        elif date_range <= 3650:  # до 10 лет
            return 90  # ежеквартально
        else:  # более 10 лет
            return 180  # каждые полгода

    def _filter_data_by_date(self,
                             start_date: datetime,
                             end_date: datetime):
        """
        Фильтрует данные по диапазону дат
        """
        direct_filtered = self.direct_estimations[
            (self.direct_estimations.index >= start_date) &
            (self.direct_estimations.index <= end_date)
            ]

        surveys_filtered = self.surveys[
            (self.surveys['date'] >= start_date) &
            (self.surveys['date'] <= end_date)
            ]

        return direct_filtered, surveys_filtered

    def _add_date_labels(self, ax, dates, values, color, offset_x=0.02, offset_y=0.02, fontsize=8):
        """
        Добавляет подписи дат справа от каждой точки

        Args:
            ax: оси графика
            dates: массив дат
            values: массив значений
            color: цвет подписей
            offset_x: смещение по X (в долях от ширины графика)
            offset_y: смещение по Y (в долях от высоты графика)
            fontsize: размер шрифта
        """
        if len(dates) == 0:
            return

        # Получаем границы графика для расчета смещения
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]

        # Добавляем подписи для каждой точки
        for date, value in zip(dates, values):
            # Форматируем дату как строку
            date_str = pd.Timestamp(date).strftime('%Y-%m-%d')

            # Рассчитываем позицию для подписи (справа от точки)
            x_pos = date + pd.Timedelta(days=x_range * offset_x)
            y_pos = value + y_range * offset_y

            # Добавляем подпись
            ax.annotate(date_str,
                        xy=(date, value),
                        xytext=(x_pos, y_pos),
                        color=color,
                        fontsize=fontsize,
                        alpha=0.8,
                        weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3',
                                  facecolor='white',
                                  edgecolor=color,
                                  alpha=0.7),
                        arrowprops=dict(arrowstyle='->',
                                        connectionstyle='arc3,rad=0.1',
                                        color=color,
                                        alpha=0.5,
                                        lw=0.5))

    def plot_timeseries(self,
                        variable: str = 'observable',
                        figsize: Tuple[int, int] = (16, 8),
                        title: Optional[str] = None,
                        xlabel: str = 'Date',
                        ylabel: str = 'Inflation',
                        color_direct: str = '#2E86C1',
                        color_survey: str = '#E74C3C',
                        marker_direct: str = 'o',
                        marker_survey: str = 's',
                        linestyle_direct: str = '-',
                        linestyle_survey: str = '-',
                        markersize: int = 8,
                        linewidth: int = 2,
                        alpha: float = 0.7,
                        show_ci: bool = True,
                        ci_alpha: float = 0.2,
                        grid: bool = True,
                        legend_loc: str = 'best',
                        save_path: Optional[Path] = None,
                        show: bool = True,
                        start_date: Optional[Union[str, datetime]] = None,
                        end_date: Optional[Union[str, datetime]] = None,
                        use_intersection: bool = False,
                        auto_format_dates: bool = True,
                        show_date_labels: bool = False,
                        date_labels_for: str = 'both',  # 'direct', 'survey', 'both'
                        label_fontsize: int = 8,
                        label_offset_x: float = 0.02,
                        label_offset_y: float = 0.02):
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
            start_date: начальная дата для отображения
            end_date: конечная дата для отображения
            use_intersection: использовать пересечение диапазонов данных
            auto_format_dates: автоматически форматировать даты
            show_date_labels: показывать подписи дат справа от точек
            date_labels_for: для каких рядов показывать подписи ('direct', 'survey', 'both')
            label_fontsize: размер шрифта подписей
            label_offset_x: смещение подписей по X
            label_offset_y: смещение подписей по Y
        """
        # Проверяем наличие данных
        if variable == 'observable':
            direct_col = 'observable_inflation'
            survey_col = 'obs_mean'
            survey_std_col = 'obs_std'
            default_title = 'Observable Inflation: Direct Estimations vs Surveys'
        else:
            direct_col = 'expected_inflation'
            survey_col = 'exp_mean'
            survey_std_col = 'exp_std'
            default_title = 'Expected Inflation: Direct Estimations vs Surveys'

        if title is None:
            title = default_title

        # Определяем диапазон дат
        start, end = self._get_date_range(start_date, end_date, use_intersection)

        # Фильтруем данные
        direct_filtered, surveys_filtered = self._filter_data_by_date(start, end)

        # Проверяем, остались ли данные после фильтрации
        if direct_filtered.empty and surveys_filtered.empty:
            print("⚠️ Нет данных в выбранном диапазоне дат")
            return None, None

        # Создаем график
        fig, ax = plt.subplots(figsize=figsize)

        # Direct estimations
        if not direct_filtered.empty:
            ax.plot(direct_filtered.index,
                    direct_filtered[direct_col],
                    marker=marker_direct,
                    linestyle=linestyle_direct,
                    color=color_direct,
                    linewidth=linewidth,
                    markersize=markersize,
                    alpha=alpha,
                    label='Real surveys')

        # Surveys
        if not surveys_filtered.empty:
            ax.plot(surveys_filtered['date'],
                    surveys_filtered[survey_col],
                    marker=marker_survey,
                    linestyle=linestyle_survey,
                    color=color_survey,
                    linewidth=linewidth,
                    markersize=markersize,
                    alpha=alpha,
                    label='Model results')

            # Доверительные интервалы для surveys
            if show_ci and survey_std_col in surveys_filtered.columns:
                ax.fill_between(surveys_filtered['date'],
                                surveys_filtered[survey_col] - surveys_filtered[survey_std_col],
                                surveys_filtered[survey_col] + surveys_filtered[survey_std_col],
                                alpha=ci_alpha,
                                color=color_survey,
                                label='Survey CI')

        # Добавляем подписи дат справа от точек
        if show_date_labels:
            # Для direct estimations
            if date_labels_for in ['direct', 'both'] and not direct_filtered.empty:
                self._add_date_labels(
                    ax,
                    direct_filtered.index,
                    direct_filtered[direct_col],
                    color_direct,
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

            # Для surveys
            if date_labels_for in ['survey', 'both'] and not surveys_filtered.empty:
                self._add_date_labels(
                    ax,
                    surveys_filtered['date'],
                    surveys_filtered[survey_col],
                    color_survey,
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

        # Настройки графика
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)

        if grid:
            ax.grid(True, alpha=0.3)

        ax.legend(loc=legend_loc)

        # Автоматическое форматирование дат
        if auto_format_dates:
            date_format = self._determine_date_format(start, end)
            tick_interval = self._determine_tick_interval(start, end)

            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))

            # Устанавливаем границы оси X с небольшим запасом для подписей
            if show_date_labels:
                x_range = (end - start).days
                padding = x_range * 0.1  # 10% запас
                ax.set_xlim(start - pd.Timedelta(days=padding),
                            end + pd.Timedelta(days=padding))
            else:
                ax.set_xlim(start, end)

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
                  figsize: Tuple[int, int] = (14, 12),
                  save_prefix: Optional[str] = None,
                  start_date: Optional[Union[str, datetime]] = None,
                  end_date: Optional[Union[str, datetime]] = None,
                  use_intersection: bool = False,
                  show_date_labels: bool = False,
                  date_labels_for: str = 'both',
                  **kwargs):
        """
        Строит два графика: для observable и expected инфляции

        Args:
            figsize: размер фигуры
            save_prefix: префикс для сохранения
            start_date: начальная дата для отображения
            end_date: конечная дата для отображения
            use_intersection: использовать пересечение диапазонов данных
            show_date_labels: показывать подписи дат справа от точек
            date_labels_for: для каких рядов показывать подписи
            **kwargs: дополнительные параметры для plot_timeseries
        """
        fig, axes = plt.subplots(2, 1, figsize=figsize)

        # Observable
        self._plot_on_axes(axes[0], 'observable',
                           start_date=start_date,
                           end_date=end_date,
                           use_intersection=use_intersection,
                           show_date_labels=show_date_labels,
                           date_labels_for=date_labels_for,
                           **kwargs)

        # Expected
        self._plot_on_axes(axes[1], 'expected',
                           start_date=start_date,
                           end_date=end_date,
                           use_intersection=use_intersection,
                           show_date_labels=show_date_labels,
                           date_labels_for=date_labels_for,
                           **kwargs)

        plt.tight_layout()

        if save_prefix:
            start, end = self._get_date_range(start_date, end_date, use_intersection)
            filename = f'{save_prefix}_both_{start.strftime("%Y%m%d")}_{end.strftime("%Y%m%d")}.png'
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✅ График сохранен: {filename}")

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

        # Извлекаем параметры
        start_date = kwargs.get('start_date', None)
        end_date = kwargs.get('end_date', None)
        use_intersection = kwargs.get('use_intersection', False)
        color_direct = kwargs.get('color_direct', '#2E86C1')
        color_survey = kwargs.get('color_survey', '#E74C3C')
        marker_direct = kwargs.get('marker_direct', 'o')
        marker_survey = kwargs.get('marker_survey', 's')
        show_ci = kwargs.get('show_ci', True)
        ci_alpha = kwargs.get('ci_alpha', 0.2)
        alpha = kwargs.get('alpha', 0.7)
        grid = kwargs.get('grid', True)
        legend_loc = kwargs.get('legend_loc', 'best')
        show_date_labels = kwargs.get('show_date_labels', False)
        date_labels_for = kwargs.get('date_labels_for', 'both')
        label_fontsize = kwargs.get('label_fontsize', 8)
        label_offset_x = kwargs.get('label_offset_x', 0.02)
        label_offset_y = kwargs.get('label_offset_y', 0.02)

        # Определяем диапазон дат
        start, end = self._get_date_range(start_date, end_date, use_intersection)

        # Фильтруем данные
        direct_filtered, surveys_filtered = self._filter_data_by_date(start, end)

        # Direct estimations
        if not direct_filtered.empty:
            ax.plot(direct_filtered.index,
                    direct_filtered[direct_col],
                    marker=marker_direct,
                    linestyle='-',
                    color=color_direct,
                    linewidth=2,
                    markersize=6,
                    alpha=alpha,
                    label='Direct Estimations')

        # Surveys
        if not surveys_filtered.empty:
            ax.plot(surveys_filtered['date'],
                    surveys_filtered[survey_col],
                    marker=marker_survey,
                    linestyle='-',
                    color=color_survey,
                    linewidth=2,
                    markersize=6,
                    alpha=alpha,
                    label='Surveys (Quarterly)')

            # Доверительные интервалы
            if show_ci and survey_std_col in surveys_filtered.columns:
                ax.fill_between(surveys_filtered['date'],
                                surveys_filtered[survey_col] - surveys_filtered[survey_std_col],
                                surveys_filtered[survey_col] + surveys_filtered[survey_std_col],
                                alpha=ci_alpha,
                                color=color_survey,
                                label='Survey CI')

        # Добавляем подписи дат
        if show_date_labels:
            if date_labels_for in ['direct', 'both'] and not direct_filtered.empty:
                self._add_date_labels(
                    ax,
                    direct_filtered.index,
                    direct_filtered[direct_col],
                    color_direct,
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

            if date_labels_for in ['survey', 'both'] and not surveys_filtered.empty:
                self._add_date_labels(
                    ax,
                    surveys_filtered['date'],
                    surveys_filtered[survey_col],
                    color_survey,
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Date', fontsize=10)
        ax.set_ylabel('Inflation', fontsize=10)

        if grid:
            ax.grid(True, alpha=0.3)

        ax.legend(loc=legend_loc)

        # Автоматическое форматирование дат
        date_format = self._determine_date_format(start, end)
        tick_interval = self._determine_tick_interval(start, end)

        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))

        # Устанавливаем границы оси X с запасом для подписей
        if show_date_labels:
            x_range = (end - start).days
            padding = x_range * 0.1
            ax.set_xlim(start - pd.Timedelta(days=padding),
                        end + pd.Timedelta(days=padding))
        else:
            ax.set_xlim(start, end)

        # Поворачиваем подписи
        fig = ax.get_figure()
        fig.autofmt_xdate()