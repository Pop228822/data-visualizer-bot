"""
Создание графиков на Plotly: современный вид и поддержка больших данных
"""
import io
from typing import Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Лимиты для больших данных (всегда агрегируем/ограничиваем)
MAX_POINTS_LINE = 2000
MAX_BAR_CATEGORIES = 25
MAX_PIE_SLICES = 12
HISTOGRAM_MAX_BINS = 60

# Единый стиль (title задаётся в _apply_layout). Увеличенные отступы, чтобы подписи не обрезались.
CHART_LAYOUT = dict(
    template="plotly_white",
    font=dict(family="Inter, system-ui, sans-serif", size=12),
    margin=dict(l=70, r=50, t=70, b=100),
    height=520,
    width=920,
    paper_bgcolor="rgba(255,255,255,1)",
    plot_bgcolor="rgba(248,249,250,1)",
    xaxis=dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
        automargin=True,
        title=dict(standoff=10),
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        zeroline=False,
        automargin=True,
        title=dict(standoff=10),
    ),
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
)

COLORS_BAR = px.colors.qualitative.Set2
COLORS_LINE = px.colors.qualitative.Set1
# Для круговой диаграммы нужен длинный список (до MAX_PIE_SLICES)
COLORS_PIE = list(px.colors.qualitative.Set3) + list(px.colors.qualitative.Pastel)[:4]


def _fig_to_png_bytes(fig: go.Figure) -> io.BytesIO:
    """Рендер графика в PNG (высокое разрешение для чёткости в мессенджере)."""
    buf = io.BytesIO()
    fig.write_image(buf, format="png", scale=2, engine="kaleido")
    buf.seek(0)
    return buf


def _apply_layout(fig: go.Figure, title: str) -> None:
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=16), x=0.5, xanchor="center"),
    )


class PlotGenerator:
    """Генератор графиков на Plotly: вау-визуализация и работа с большими данными."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def create_bar_plot(
        self,
        x: str,
        y: Optional[str] = None,
        title: Optional[str] = None,
        max_categories: int = MAX_BAR_CATEGORIES,
    ) -> io.BytesIO:
        """Столбчатая диаграмма: топ категорий, аккуратные подписи."""
        if y:
            plot_df = self.df[[x, y]].dropna()
            if len(plot_df) > max_categories * 2:
                plot_df = plot_df.groupby(x, as_index=False)[y].sum().nlargest(max_categories, y)
            fig = px.bar(plot_df, x=x, y=y, color=y, color_continuous_scale="Blues", text_auto=".0f")
            fig.update_traces(textposition="outside", texttemplate="%{y:.0f}", cliponaxis=False)
            categories = plot_df[x].tolist()
        else:
            vc = self.df[x].value_counts()
            if len(vc) > max_categories:
                vc = vc.head(max_categories)
            plot_df = vc.reset_index()
            plot_df.columns = [x, "count"]
            fig = px.bar(plot_df, x=x, y="count", color="count", color_continuous_scale="Teal", text_auto=".0f")
            fig.update_traces(textposition="outside", texttemplate="%{y:.0f}", cliponaxis=False)
            categories = plot_df[x].tolist()
        # Показать подпись под каждым столбцом: явно задаём все метки (Plotly иначе выводит каждую вторую)
        tickvals = categories
        ticktext = [str(c) for c in categories]
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_ticklabeloverflow="allow",
            xaxis_tickmode="array",
            xaxis_tickvals=tickvals,
            xaxis_ticktext=ticktext,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title=x,
            yaxis_title=y or "Количество",
        )
        _apply_layout(fig, title or f"Диаграмма: {x}")
        return _fig_to_png_bytes(fig)

    def create_histogram(self, column: str, bins: int = 30, title: Optional[str] = None) -> io.BytesIO:
        """Гистограмма с автоматическим числом столбцов при больших данных."""
        data = self.df[column].dropna()
        if len(data) > 100_000:
            data = data.sample(n=50_000, random_state=42)
        bins = min(bins, HISTOGRAM_MAX_BINS, max(10, len(data) // 50))
        fig = px.histogram(x=data, nbins=bins, color_discrete_sequence=[COLORS_BAR[0]])
        # Подписать каждый столбик числом наблюдений (y в trace — это как раз количества)
        fig.update_traces(
            marker_line_width=0.5,
            marker_line_color="white",
            text=fig.data[0].y,
            textposition="outside",
            texttemplate="%{text:.0f}",
            cliponaxis=False,
        )
        _apply_layout(fig, title or f"Гистограмма: {column}")
        fig.update_layout(
            showlegend=False,
            xaxis_title=column,
            yaxis_title="Количество",
        )
        return _fig_to_png_bytes(fig)

    def create_date_plot(self, column: str, title: Optional[str] = None) -> io.BytesIO:
        """Визуализация дат: агрегация по периоду, плавная линия или столбцы."""
        ser = pd.to_datetime(self.df[column].dropna(), errors="coerce").dropna()
        if ser.empty:
            raise ValueError(f"В колонке {column} нет корректных дат")
        days_span = (ser.max() - ser.min()).days
        if days_span <= 31:
            freq = "D"
        elif days_span <= 365:
            freq = "W"
        else:
            freq = "ME"
        agg = ser.dt.to_period(freq).value_counts().sort_index()
        agg.index = agg.index.to_timestamp()
        plot_df = agg.reset_index()
        plot_df.columns = ["date", "count"]
        if len(plot_df) <= 35:
            fig = px.bar(
                plot_df, x="date", y="count", color="count",
                color_continuous_scale="Blues", text_auto=".0f",
            )
            fig.update_traces(textposition="outside", texttemplate="%{y:.0f}", cliponaxis=False)
            fig.update_layout(coloraxis_showscale=False)
        else:
            fig = px.line(plot_df, x="date", y="count", markers=True)
            fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
        _apply_layout(fig, title or f"Распределение по датам: {column}")
        fig.update_layout(
            xaxis_title=column,
            yaxis_title="Количество записей",
            showlegend=False,
        )
        return _fig_to_png_bytes(fig)

    def create_pie_plot(self, column: str, title: Optional[str] = None) -> io.BytesIO:
        """Круговая диаграмма: топ срезов, остальное в «Прочее» при большом числе категорий."""
        vc = self.df[column].value_counts()
        if len(vc) > MAX_PIE_SLICES:
            top = vc.head(MAX_PIE_SLICES - 1)
            other_count = vc.iloc[MAX_PIE_SLICES - 1 :].sum()
            vc = pd.concat([top, pd.Series({"Прочее": other_count})])
        labels = vc.index.astype(str).tolist()
        values = vc.values.tolist()
        colors = (COLORS_PIE * ((len(labels) // len(COLORS_PIE)) + 1))[: len(labels)]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.45,
                    marker=dict(colors=colors, line=dict(color="white", width=1.5)),
                    textinfo="label+percent",
                    textposition="outside",
                    insidetextorientation="radial",
                )
            ]
        )
        _apply_layout(fig, title or f"Распределение: {column}")
        fig.update_layout(
            showlegend=False,
            height=560,
            margin=dict(l=80, r=80, t=70, b=80),
            annotations=[],  # чтобы подписи секторов не конфликтовали с layout
        )
        # Подписи на секторах: показывать и название, и процент
        fig.update_traces(
            textinfo="label+percent",
            textposition="outside",
            insidetextorientation="radial",
            textfont=dict(size=11),
        )
        return _fig_to_png_bytes(fig)

    def create_line_plot(self, x: str, y: str, title: Optional[str] = None) -> io.BytesIO:
        """Линейный график с прореживанием при большом числе точек."""
        plot_df = self.df[[x, y]].dropna()
        if len(plot_df) > MAX_POINTS_LINE:
            plot_df = plot_df.iloc[:: len(plot_df) // MAX_POINTS_LINE]
        fig = px.line(plot_df, x=x, y=y)
        fig.update_traces(line=dict(width=2.5))
        fig.update_layout(xaxis_title=x, yaxis_title=y)
        _apply_layout(fig, title or f"{y} по {x}")
        return _fig_to_png_bytes(fig)

    def create_scatter_plot(self, x: str, y: str, title: Optional[str] = None) -> io.BytesIO:
        """Точечная диаграмма с ограничением точек и полупрозрачностью."""
        plot_df = self.df[[x, y]].dropna()
        if len(plot_df) > MAX_POINTS_LINE:
            plot_df = plot_df.sample(n=MAX_POINTS_LINE, random_state=42)
        fig = px.scatter(plot_df, x=x, y=y, opacity=0.6)
        fig.update_traces(marker=dict(size=6, line=dict(width=0)))
        fig.update_layout(xaxis_title=x, yaxis_title=y)
        _apply_layout(fig, title or f"Диаграмма рассеяния: {y} vs {x}")
        return _fig_to_png_bytes(fig)

    def create_auto_visualization(self, column: str) -> Tuple[io.BytesIO, str]:
        """Автовыбор типа графика по типу данных."""
        is_numeric = pd.api.types.is_numeric_dtype(self.df[column])
        unique_count = self.df[column].nunique()
        if is_numeric:
            if unique_count > 20:
                return self.create_histogram(column), "Гистограмма"
            return self.create_bar_plot(column), "Столбчатая диаграмма"
        if unique_count <= 8 and unique_count > 1:
            return self.create_pie_plot(column), "Круговая диаграмма"
        top = self.df[column].value_counts().head(10)
        temp_df = pd.DataFrame({column: top.index, "count": top.values})
        gen = PlotGenerator(temp_df)
        return gen.create_bar_plot(column, "count"), "Столбчатая диаграмма (топ-10)"
