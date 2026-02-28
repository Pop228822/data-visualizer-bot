"""
Создание графиков и визуализаций
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict, Any, Tuple
import io

# Настройка стиля
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10


class PlotGenerator:
    """Класс для генерации графиков"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Инициализация генератора графиков
        
        Args:
            df: DataFrame с данными
        """
        self.df = df
    
    def create_line_plot(self, x: str, y: str, title: Optional[str] = None) -> io.BytesIO:
        """
        Создать линейный график
        
        Args:
            x: Название колонки для оси X
            y: Название колонки для оси Y
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(10, 6))
        plt.plot(self.df[x], self.df[y])
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(title or f"{y} по {x}")
        plt.grid(True)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_bar_plot(
        self,
        x: str,
        y: Optional[str] = None,
        title: Optional[str] = None,
        max_categories: int = 20,
    ) -> io.BytesIO:
        """
        Создать столбчатую диаграмму. При большом числе категорий показывается только топ max_categories.
        
        Args:
            x: Название колонки для оси X
            y: Название колонки для оси Y (опционально)
            title: Заголовок графика
            max_categories: Максимум столбцов (для читаемости при больших данных)
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(10, 6))
        
        if y:
            self.df.plot(x=x, y=y, kind='bar', ax=plt.gca())
        else:
            vc = self.df[x].value_counts()
            if len(vc) > max_categories:
                vc = vc.head(max_categories)
            vc.plot(kind='bar', ax=plt.gca())
        
        plt.xlabel(x)
        plt.ylabel(y or "Количество")
        plt.title(title or f"Диаграмма: {x}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_date_plot(self, column: str, title: Optional[str] = None) -> io.BytesIO:
        """
        Визуализация для колонки с датами: агрегация по периоду (день/неделя/месяц)
        и отображение количества записей — линейный график или столбчатая по периодам.
        
        Args:
            column: Название колонки с датами
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        ser = pd.to_datetime(self.df[column].dropna(), errors='coerce').dropna()
        if ser.empty:
            raise ValueError(f"В колонке {column} нет корректных дат")
        
        # Определяем период агрегации по размаху дат
        days_span = (ser.max() - ser.min()).days
        if days_span <= 31:
            freq = 'D'  # по дням
            date_format = '%d.%m'
        elif days_span <= 365:
            freq = 'W'  # по неделям
            date_format = '%d.%m'
        else:
            freq = 'ME'  # month end (месяц)
            date_format = '%b %Y'
        
        agg = ser.dt.to_period(freq).value_counts().sort_index()
        agg.index = agg.index.to_timestamp()
        
        plt.figure(figsize=(10, 6))
        if len(agg) <= 31:
            agg.plot(kind='bar', ax=plt.gca(), width=0.8)
            plt.xticks(rotation=45, ha='right')
        else:
            agg.plot(kind='line', ax=plt.gca(), marker='o', markersize=4)
            plt.grid(True, alpha=0.3)
        
        plt.xlabel(column)
        plt.ylabel("Количество записей")
        plt.title(title or f"Распределение по датам: {column}")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_pie_plot(self, column: str, title: Optional[str] = None) -> io.BytesIO:
        """
        Создать круговую диаграмму
        
        Args:
            column: Название колонки для группировки
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(8, 8))
        value_counts = self.df[column].value_counts()
        plt.pie(value_counts.values, labels=value_counts.index, autopct='%1.1f%%')
        plt.title(title or f"Распределение: {column}")
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_scatter_plot(self, x: str, y: str, title: Optional[str] = None) -> io.BytesIO:
        """
        Создать диаграмму рассеяния
        
        Args:
            x: Название колонки для оси X
            y: Название колонки для оси Y
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(10, 6))
        plt.scatter(self.df[x], self.df[y], alpha=0.6)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.title(title or f"Диаграмма рассеяния: {y} vs {x}")
        plt.grid(True)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_histogram(self, column: str, bins: int = 30, title: Optional[str] = None) -> io.BytesIO:
        """
        Создать гистограмму
        
        Args:
            column: Название колонки
            bins: Количество интервалов
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(10, 6))
        plt.hist(self.df[column].dropna(), bins=bins, edgecolor='black')
        plt.xlabel(column)
        plt.ylabel("Частота")
        plt.title(title or f"Гистограмма: {column}")
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        return buf
    
    def create_auto_visualization(self, column: str) -> tuple[io.BytesIO, str]:
        """
        Автоматически создать подходящую визуализацию для колонки
        
        Args:
            column: Название колонки
            
        Returns:
            Кортеж (BytesIO объект с изображением, название типа визуализации)
        """
        import pandas as pd
        
        is_numeric = pd.api.types.is_numeric_dtype(self.df[column])
        unique_count = self.df[column].nunique()
        
        if is_numeric:
            if unique_count > 20:
                return self.create_histogram(column), "Гистограмма"
            else:
                return self.create_bar_plot(column), "Столбчатая диаграмма"
        else:
            if unique_count <= 8 and unique_count > 1:
                return self.create_pie_plot(column), "Круговая диаграмма"
            else:
                # Для категорий с большим количеством значений показываем топ-10
                top_values = self.df[column].value_counts().head(10)
                temp_df = pd.DataFrame({column: top_values.index, 'count': top_values.values})
                plot_generator = PlotGenerator(temp_df)
                return plot_generator.create_bar_plot(column, 'count'), "Столбчатая диаграмма (топ-10)"