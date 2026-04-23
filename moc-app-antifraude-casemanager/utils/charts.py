"""Centralized Plotly chart styling helpers."""
import plotly.graph_objects as go
import plotly.express as px

_FONT = dict(family="Inter, Arial, sans-serif", color="#0D1B2A", size=12)
_TITLE_FONT = dict(family="Inter, Arial, sans-serif", color="#0D1B2A", size=14)
_AXIS = dict(color="#374151", tickfont=dict(color="#374151", size=11), gridcolor="#E8EEF6", linecolor="#D0DCF0")

PALETTE_BLUE   = ["#1565C0", "#1976D2", "#42A5F5", "#90CAF9", "#BBDEFB"]
PALETTE_STATUS = {"Aberto": "#1976D2", "Em Investigação": "#F57C00",
                  "Aguardando Documentação": "#7B1FA2", "Encerrado": "#388E3C", "Escalado": "#D32F2F"}
PALETTE_PRIORITY = {"Crítica": "#C62828", "Alta": "#EF6C00", "Média": "#F9A825", "Baixa": "#2E7D32"}


def base_layout(title: str = "", height: int = 340, show_legend: bool = False) -> dict:
    return dict(
        title=dict(text=title, font=_TITLE_FONT, x=0, xanchor="left", pad=dict(l=4, b=8)),
        font=_FONT,
        height=height,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        showlegend=show_legend,
        margin=dict(l=8, r=8, t=44, b=8),
        xaxis=_AXIS,
        yaxis=_AXIS,
        hoverlabel=dict(bgcolor="#0D1B2A", font_color="#FFFFFF", font_size=12, bordercolor="#0D1B2A"),
    )


def apply_chart_style(fig: go.Figure, title: str = "", height: int = 340,
                      show_legend: bool = False) -> go.Figure:
    layout = base_layout(title, height, show_legend)
    fig.update_layout(**layout)
    fig.update_xaxes(showgrid=True, gridcolor="#E8EEF6", linecolor="#D0DCF0",
                     tickfont=dict(color="#374151", size=11), title_font=dict(color="#374151"))
    fig.update_yaxes(showgrid=True, gridcolor="#E8EEF6", linecolor="#D0DCF0",
                     tickfont=dict(color="#374151", size=11), title_font=dict(color="#374151"))
    return fig


def bar_chart(df, x, y, title="", color=None, color_map=None, height=340,
              orientation="v", barmode="relative") -> go.Figure:
    kwargs = dict(color_discrete_sequence=PALETTE_BLUE)
    if color:
        kwargs["color"] = color
    if color_map:
        kwargs["color_discrete_map"] = color_map
    fig = px.bar(df, x=x, y=y, orientation=orientation, barmode=barmode, **kwargs)
    fig.update_traces(marker_line_width=0)
    apply_chart_style(fig, title, height, show_legend=bool(color and color_map))
    return fig


def donut_chart(df, names, values, title="", height=360) -> go.Figure:
    fig = px.pie(df, names=names, values=values, hole=0.45)
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        textfont=dict(color="#0D1B2A", size=11),
        marker=dict(line=dict(color="#FFFFFF", width=2)),
        pull=[0.02] * len(df),
    )
    fig.update_layout(
        title=dict(text=title, font=_TITLE_FONT, x=0, xanchor="left"),
        font=_FONT,
        height=height,
        paper_bgcolor="#FFFFFF",
        showlegend=True,
        legend=dict(
            orientation="v",
            x=1.02, y=0.5,
            font=dict(color="#0D1B2A", size=11),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=8, r=180, t=44, b=8),
    )
    return fig


def area_chart(df, x, y, title="", height=340) -> go.Figure:
    fig = px.area(df, x=x, y=y, color_discrete_sequence=["#1565C0"])
    fig.update_traces(line=dict(color="#1565C0", width=2.5), fillcolor="rgba(21,101,192,0.12)")
    apply_chart_style(fig, title, height)
    return fig


def heatmap(z, x, y, title="", height=380, text=None) -> go.Figure:
    kwargs = {}
    if text is not None:
        kwargs["text"] = text
        kwargs["texttemplate"] = "%{text}"
        kwargs["textfont"] = {"size": 11, "color": "#0D1B2A"}
    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y,
        colorscale="Blues",
        hovertemplate="%{y} / %{x}: %{z}<extra></extra>",
        **kwargs,
    ))
    fig.update_layout(
        title=dict(text=title, font=_TITLE_FONT, x=0, xanchor="left"),
        font=_FONT,
        height=height,
        paper_bgcolor="#FFFFFF",
        margin=dict(l=8, r=8, t=44, b=8),
        xaxis=dict(tickfont=dict(color="#0D1B2A", size=11), title_font=dict(color="#374151")),
        yaxis=dict(tickfont=dict(color="#0D1B2A", size=11), title_font=dict(color="#374151")),
    )
    return fig
