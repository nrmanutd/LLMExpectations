from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional, Tuple, Union, List, Dict, Any
from datetime import datetime


class TimeSeriesVisualizer:
    """
    Класс для визуализации временных рядов с несинхронизированными датами
    Поддерживает один истинный ряд и несколько модельных рядов
    """

    def __init__(self,
                 true_series: pd.DataFrame,
                 model_series: Dict[str, pd.DataFrame]):
        """
        Args:
            true_series: DataFrame с колонками 'observable_inflation', 'expected_inflation'
                        Индекс - даты (истинный ряд)
            model_series: Словарь {имя_модели: DataFrame с колонками 'obs_mean', 'exp_mean'}
                         Индекс - даты (модельные ряды)
        """
        self.true_series = true_series.copy()
        self.model_series = {}

        # Приводим даты к datetime для истинного ряда
        if not pd.api.types.is_datetime64_any_dtype(self.true_series.index):
            self.true_series.index = pd.to_datetime(self.true_series.index)
        self.true_series = self.true_series.sort_index()

        # Приводим даты к datetime для каждого модельного ряда
        for name, df in model_series.items():
            self.model_series[name] = df.copy()
            if not pd.api.types.is_datetime64_any_dtype(self.model_series[name].index):
                self.model_series[name].index = pd.to_datetime(self.model_series[name].index)
            self.model_series[name] = self.model_series[name].sort_index()

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
        # Получаем все даты из всех рядов
        all_dates = [self.true_series.index]
        for df in self.model_series.values():
            all_dates.append(df.index)

        # Проверяем, что данные не пустые
        if not all_dates:
            print("⚠️ Нет данных")
            return datetime.now(), datetime.now()

        # Находим глобальные минимумы и максимумы
        all_min = min(dates.min() for dates in all_dates if len(dates) > 0)
        all_max = max(dates.max() for dates in all_dates if len(dates) > 0)

        if use_intersection:
            # Находим пересечение всех диапазонов
            raw_start = max(dates.min() for dates in all_dates if len(dates) > 0)
            raw_end = min(dates.max() for dates in all_dates if len(dates) > 0)

            if raw_start > raw_end:
                print("⚠️ Ряды данных не пересекаются во времени")
                mid_point = all_min + (all_max - all_min) / 2
                return mid_point - pd.Timedelta(days=30), mid_point + pd.Timedelta(days=30)

            # Определяем самый широкий ряд
            max_range = -1
            widest_dates = None
            for dates in all_dates:
                if len(dates) > 0:
                    date_range = (dates.max() - dates.min()).days
                    if date_range > max_range:
                        max_range = date_range
                        widest_dates = dates

            if widest_dates is not None:
                # Расширяем самый широкий ряд на одну точку с каждой стороны
                left_dates = widest_dates[widest_dates < raw_start]
                if len(left_dates) > 0:
                    start = left_dates[-1]
                else:
                    start = raw_start

                right_dates = widest_dates[widest_dates > raw_end]
                if len(right_dates) > 0:
                    end = right_dates[0]
                else:
                    end = raw_end
            else:
                start = raw_start
                end = raw_end

        else:
            # Используем объединение всех диапазонов
            start = all_min
            end = all_max

        # Применяем пользовательские ограничения
        if start_date is not None:
            start_date = pd.to_datetime(start_date)
            start = max(start, start_date)

        if end_date is not None:
            end_date = pd.to_datetime(end_date)
            end = min(end, end_date)

        if start > end:
            print(f"⚠️ Начальная дата ({start}) позже конечной ({end}). Меняем местами.")
            start, end = end, start

        return start, end

    def _determine_date_format(self, start_date: datetime, end_date: datetime) -> str:
        """Определяет формат отображения дат в зависимости от длины периода"""
        date_range = (end_date - start_date).days
        if date_range <= 60:
            return '%Y-%m-%d'
        elif date_range <= 365:
            return '%Y-%m-%d'
        elif date_range <= 1825:
            return '%Y-%m-%d'
        elif date_range <= 3650:
            return '%Y-%m-%d'
        else:
            return '%Y-%m-%d'

    def _determine_tick_interval(self, start_date: datetime, end_date: datetime) -> int:
        """Определяет интервал между метками на оси X"""
        date_range = (end_date - start_date).days
        if date_range <= 60:
            return 3
        elif date_range <= 180:
            return 7
        elif date_range <= 365:
            return 14
        elif date_range <= 730:
            return 30
        elif date_range <= 1825:
            return 60
        elif date_range <= 3650:
            return 90
        else:
            return 180

    def _filter_data_by_date(self,
                             start_date: datetime,
                             end_date: datetime):
        """
        Фильтрует данные по диапазону дат
        """
        true_filtered = self.true_series[
            (self.true_series.index >= start_date) &
            (self.true_series.index <= end_date)
            ]

        model_filtered = {}
        for name, df in self.model_series.items():
            model_filtered[name] = df[
                (df.index >= start_date) &
                (df.index <= end_date)
                ]

        return true_filtered, model_filtered

    def _add_date_labels(self, ax, dates, values, color, offset_x=0.02, offset_y=0.02, fontsize=8):
        """Добавляет подписи дат справа от каждой точки"""
        if len(dates) == 0:
            return

        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]

        for date, value in zip(dates, values):
            date_str = pd.Timestamp(date).strftime('%Y-%m-%d')
            x_pos = date + pd.Timedelta(days=x_range * offset_x)
            y_pos = value + y_range * offset_y

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
                        colors: Optional[Dict[str, str]] = None,
                        markers: Optional[Dict[str, str]] = None,
                        linestyles: Optional[Dict[str, str]] = None,
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
                        date_labels_for: str = 'all',  # 'true', 'models', 'all'
                        label_fontsize: int = 8,
                        label_offset_x: float = 0.02,
                        label_offset_y: float = 0.02,
                        model_order: Optional[List[str]] = None):
        """
        Строит график временных рядов для observable или expected инфляции

        Args:
            variable: 'observable' или 'expected'
            figsize: размер фигуры
            title: заголовок
            xlabel: подпись оси X
            ylabel: подпись оси Y
            colors: словарь цветов для рядов {'true': '#color', 'model1': '#color', ...}
            markers: словарь маркеров для рядов
            linestyles: словарь стилей линий для рядов
            markersize: размер маркеров
            linewidth: толщина линии
            alpha: прозрачность
            show_ci: показывать доверительные интервалы
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
            date_labels_for: для каких рядов показывать подписи ('true', 'models', 'all')
            label_fontsize: размер шрифта подписей
            label_offset_x: смещение подписей по X
            label_offset_y: смещение подписей по Y
            model_order: порядок отображения моделей в легенде
        """
        # Определяем колонки
        if variable == 'observable':
            true_col = 'observable_inflation'
            model_col = 'obs_mean'
            model_std_col = 'obs_std'
            default_title = f'Observable Inflation: True vs Models'
        else:
            true_col = 'expected_inflation'
            model_col = 'exp_mean'
            model_std_col = 'exp_std'
            default_title = f'Expected Inflation: True vs Models'

        if title is None:
            title = default_title

        # Настройки по умолчанию для цветов и маркеров
        default_colors = {
            'true': '#2E86C1',  # синий
        }
        # Цвета для моделей из палитры
        model_colors = [
            '#E74C3C',  # красный
            '#2ECC71',  # зеленый
            '#F39C12',  # оранжевый
            '#9B59B6',  # фиолетовый
            '#1ABC9C',  # бирюзовый
            '#E67E22',  # темно-оранжевый
            '#3498DB',  # голубой
            '#E74C3C',  # розовый
        ]

        for i, name in enumerate(self.model_series.keys()):
            default_colors[name] = model_colors[i % len(model_colors)]

        default_markers = {
            'true': 'o',
        }
        model_markers = ['s', '^', 'D', '*', 'p', 'X', 'h', 'v']
        for i, name in enumerate(self.model_series.keys()):
            default_markers[name] = model_markers[i % len(model_markers)]

        default_linestyles = {
            'true': '-',
        }
        model_linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':']
        for i, name in enumerate(self.model_series.keys()):
            default_linestyles[name] = model_linestyles[i % len(model_linestyles)]

        # Применяем пользовательские настройки
        colors = colors or {}
        markers = markers or {}
        linestyles = linestyles or {}

        all_colors = {**default_colors, **colors}
        all_markers = {**default_markers, **markers}
        all_linestyles = {**default_linestyles, **linestyles}

        # Определяем диапазон дат
        start, end = self._get_date_range(start_date, end_date, use_intersection)

        # Фильтруем данные
        true_filtered, model_filtered = self._filter_data_by_date(start, end)

        # Проверяем, остались ли данные после фильтрации
        if true_filtered.empty and all(df.empty for df in model_filtered.values()):
            print("⚠️ Нет данных в выбранном диапазоне дат")
            return None, None

        # Создаем график
        fig, ax = plt.subplots(figsize=figsize)

        # Определяем порядок отображения
        if model_order is None:
            model_names = list(model_filtered.keys())
        else:
            model_names = [name for name in model_order if name in model_filtered]

        # Рисуем истинный ряд
        if not true_filtered.empty:
            ax.plot(true_filtered.index,
                    true_filtered[true_col],
                    marker=all_markers.get('true', 'o'),
                    linestyle=all_linestyles.get('true', '-'),
                    color=all_colors.get('true', '#2E86C1'),
                    linewidth=linewidth,
                    markersize=markersize,
                    alpha=alpha,
                    label='True Series')

        # Рисуем модельные ряды
        for name in model_names:
            df = model_filtered[name]
            if not df.empty:
                ax.plot(df.index,
                        df[model_col],
                        marker=all_markers.get(name, 's'),
                        linestyle=all_linestyles.get(name, '-'),
                        color=all_colors.get(name, '#E74C3C'),
                        linewidth=linewidth,
                        markersize=markersize,
                        alpha=alpha,
                        label=name)

                # Доверительные интервалы для моделей
                if show_ci and model_std_col in df.columns:
                    ax.fill_between(df.index,
                                    df[model_col] - df[model_std_col],
                                    df[model_col] + df[model_std_col],
                                    alpha=ci_alpha,
                                    color=all_colors.get(name, '#E74C3C'),
                                    label=f'{name} CI')

        # Добавляем подписи дат
        if show_date_labels:
            # Для истинного ряда
            if date_labels_for in ['true', 'all'] and not true_filtered.empty:
                self._add_date_labels(
                    ax,
                    true_filtered.index,
                    true_filtered[true_col],
                    all_colors.get('true', '#2E86C1'),
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

            # Для модельных рядов
            if date_labels_for in ['models', 'all']:
                for name in model_names:
                    df = model_filtered[name]
                    if not df.empty:
                        self._add_date_labels(
                            ax,
                            df.index,
                            df[model_col],
                            all_colors.get(name, '#E74C3C'),
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

            if show_date_labels:
                x_range = (end - start).days
                padding = x_range * 0.1
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
                  date_labels_for: str = 'all',
                  **kwargs):
        """
        Строит два графика: для observable и expected инфляции
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
        if variable == 'observable':
            true_col = 'observable_inflation'
            model_col = 'obs_mean'
            model_std_col = 'obs_std'
            title = 'Observable Inflation'
        else:
            true_col = 'expected_inflation'
            model_col = 'exp_mean'
            model_std_col = 'exp_std'
            title = 'Expected Inflation'

        start_date = kwargs.get('start_date', None)
        end_date = kwargs.get('end_date', None)
        use_intersection = kwargs.get('use_intersection', False)
        show_date_labels = kwargs.get('show_date_labels', False)
        date_labels_for = kwargs.get('date_labels_for', 'all')
        label_fontsize = kwargs.get('label_fontsize', 8)
        label_offset_x = kwargs.get('label_offset_x', 0.02)
        label_offset_y = kwargs.get('label_offset_y', 0.02)
        grid = kwargs.get('grid', True)
        legend_loc = kwargs.get('legend_loc', 'best')
        show_ci = kwargs.get('show_ci', True)
        ci_alpha = kwargs.get('ci_alpha', 0.2)
        alpha = kwargs.get('alpha', 0.7)

        # Настройки цветов
        colors = kwargs.get('colors', {})
        markers = kwargs.get('markers', {})
        linestyles = kwargs.get('linestyles', {})

        default_colors = {'true': '#2E86C1'}
        model_colors = ['#E74C3C', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22', '#3498DB']
        for i, name in enumerate(self.model_series.keys()):
            default_colors[name] = model_colors[i % len(model_colors)]

        all_colors = {**default_colors, **colors}

        start, end = self._get_date_range(start_date, end_date, use_intersection)
        true_filtered, model_filtered = self._filter_data_by_date(start, end)

        # Истинный ряд
        if not true_filtered.empty:
            ax.plot(true_filtered.index,
                    true_filtered[true_col],
                    marker='o',
                    linestyle='-',
                    color=all_colors.get('true', '#2E86C1'),
                    linewidth=2,
                    markersize=6,
                    alpha=alpha,
                    label='True Series')

        # Модельные ряды
        for name, df in model_filtered.items():
            if not df.empty:
                ax.plot(df.index,
                        df[model_col],
                        marker='s',
                        linestyle='-',
                        color=all_colors.get(name, '#E74C3C'),
                        linewidth=2,
                        markersize=6,
                        alpha=alpha,
                        label=name)

                if show_ci and model_std_col in df.columns:
                    ax.fill_between(df.index,
                                    df[model_col] - df[model_std_col],
                                    df[model_col] + df[model_std_col],
                                    alpha=ci_alpha,
                                    color=all_colors.get(name, '#E74C3C'),
                                    label=f'{name} CI')

        # Подписи дат
        if show_date_labels:
            if date_labels_for in ['true', 'all'] and not true_filtered.empty:
                self._add_date_labels(
                    ax,
                    true_filtered.index,
                    true_filtered[true_col],
                    all_colors.get('true', '#2E86C1'),
                    offset_x=label_offset_x,
                    offset_y=label_offset_y,
                    fontsize=label_fontsize
                )

            if date_labels_for in ['models', 'all']:
                for name, df in model_filtered.items():
                    if not df.empty:
                        self._add_date_labels(
                            ax,
                            df.index,
                            df[model_col],
                            all_colors.get(name, '#E74C3C'),
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

        date_format = self._determine_date_format(start, end)
        tick_interval = self._determine_tick_interval(start, end)

        ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=tick_interval))

        if show_date_labels:
            x_range = (end - start).days
            padding = x_range * 0.1
            ax.set_xlim(start - pd.Timedelta(days=padding),
                        end + pd.Timedelta(days=padding))
        else:
            ax.set_xlim(start, end)

        fig = ax.get_figure()
        fig.autofmt_xdate()
