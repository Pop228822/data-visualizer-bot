"""
Рекомендации по визуализации данных
"""
import pandas as pd
from typing import List, Dict, Any


class VisualizationRecommender:
    """Класс для рекомендации типов визуализации"""
    
    def __init__(self, df: pd.DataFrame):
        """
        Инициализация рекомендателя
        
        Args:
            df: DataFrame с данными
        """
        self.df = df
    
    def recommend_visualizations(self) -> List[Dict[str, Any]]:
        """
        Рекомендовать типы визуализации на основе данных
        
        Returns:
            Список рекомендаций с типом визуализации и обоснованием
        """
        recommendations = []
        
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Рекомендации для числовых данных
        if len(numeric_cols) >= 2:
            recommendations.append({
                "type": "scatter",
                "name": "Диаграмма рассеяния",
                "reason": f"Две или более числовых колонки ({', '.join(numeric_cols[:2])})",
                "columns": numeric_cols[:2]
            })
        
        if len(numeric_cols) >= 1:
            recommendations.append({
                "type": "line",
                "name": "Линейный график",
                "reason": f"Временные ряды или последовательные данные",
                "columns": numeric_cols[:1]
            })
            
            recommendations.append({
                "type": "bar",
                "name": "Столбчатая диаграмма",
                "reason": f"Сравнение значений по категориям",
                "columns": numeric_cols[:1]
            })
        
        # Рекомендации для категориальных данных
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            recommendations.append({
                "type": "bar",
                "name": "Столбчатая диаграмма",
                "reason": f"Группировка по категориям ({categorical_cols[0]})",
                "columns": [categorical_cols[0], numeric_cols[0]]
            })
        
        if len(categorical_cols) >= 1:
            value_counts = self.df[categorical_cols[0]].value_counts()
            if len(value_counts) <= 10:
                recommendations.append({
                    "type": "pie",
                    "name": "Круговая диаграмма",
                    "reason": f"Распределение по категориям ({categorical_cols[0]})",
                    "columns": [categorical_cols[0]]
                })
        
        return recommendations
    
    def get_best_visualization(self) -> Dict[str, Any]:
        """
        Получить лучшую рекомендацию визуализации
        
        Returns:
            Словарь с лучшей рекомендацией
        """
        recommendations = self.recommend_visualizations()
        if not recommendations:
            return {
                "type": "table",
                "name": "Таблица",
                "reason": "Недостаточно данных для визуализации",
                "columns": []
            }
        
        # Приоритет: scatter > bar > line > pie
        priority = {"scatter": 4, "bar": 3, "line": 2, "pie": 1}
        return max(recommendations, key=lambda x: priority.get(x["type"], 0))
