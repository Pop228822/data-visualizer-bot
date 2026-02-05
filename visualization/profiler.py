"""
Профилирование данных из Excel файлов
"""
import pandas as pd
from typing import Dict, Any


class DataProfiler:
    """Класс для анализа и профилирования данных"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Инициализация профилера
        
        Args:
            df: DataFrame с данными
        """
        self.df = df
    
    def get_basic_info(self) -> Dict[str, Any]:
        """
        Получить базовую информацию о данных
        
        Returns:
            Словарь с базовой информацией
        """
        return {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum(),
            "null_counts": self.df.isnull().sum().to_dict()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по числовым колонкам
        
        Returns:
            Словарь со статистикой
        """
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        if len(numeric_cols) == 0:
            return {}
        
        return self.df[numeric_cols].describe().to_dict()
    
    def detect_outliers(self, column: str) -> pd.Series:
        """
        Обнаружить выбросы в указанной колонке
        
        Args:
            column: Название колонки
            
        Returns:
            Series с булевыми значениями (True для выбросов)
        """
        if column not in self.df.columns:
            raise ValueError(f"Колонка {column} не найдена")
        
        if self.df[column].dtype not in ['int64', 'float64']:
            raise ValueError(f"Колонка {column} не числовая")
        
        Q1 = self.df[column].quantile(0.25)
        Q3 = self.df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return (self.df[column] < lower_bound) | (self.df[column] > upper_bound)
    
    def get_column_info(self, column: str) -> Dict[str, Any]:
        """
        Получить детальную информацию о колонке
        
        Args:
            column: Название колонки
            
        Returns:
            Словарь с информацией о колонке
        """
        if column not in self.df.columns:
            raise ValueError(f"Колонка {column} не найдена")
        
        info = {
            "name": column,
            "dtype": str(self.df[column].dtype),
            "null_count": self.df[column].isnull().sum(),
            "unique_count": self.df[column].nunique()
        }
        
        if self.df[column].dtype in ['int64', 'float64']:
            info.update({
                "mean": self.df[column].mean(),
                "median": self.df[column].median(),
                "std": self.df[column].std(),
                "min": self.df[column].min(),
                "max": self.df[column].max()
            })
        
        return info
