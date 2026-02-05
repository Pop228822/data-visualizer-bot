"""
Создание графиков и визуализаций
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Dict, Any
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
    
    def create_bar_plot(self, x: str, y: Optional[str] = None, title: Optional[str] = None) -> io.BytesIO:
        """
        Создать столбчатую диаграмму
        
        Args:
            x: Название колонки для оси X
            y: Название колонки для оси Y (опционально)
            title: Заголовок графика
            
        Returns:
            BytesIO объект с изображением
        """
        plt.figure(figsize=(10, 6))
        
        if y:
            self.df.plot(x=x, y=y, kind='bar', ax=plt.gca())
        else:
            self.df[x].value_counts().plot(kind='bar', ax=plt.gca())
        
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
