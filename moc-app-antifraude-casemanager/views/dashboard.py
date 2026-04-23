import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from utils.formatting import format_currency, format_percentage
from utils.constants import STATUS_OPTIONS, PRIORITY_OPTIONS, FRAUD_TYPES, CHANNELS, QUEUES, ALERT_SOURCES
from utils.charts import bar_chart, donut_chart, area_chart, heatmap, PALETTE_STATUS, PALETTE_PRIORITY
from components.styles import metric_card, section_header


def render_dashboard(ds):
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("📊 Dashboard Executivo")
        st.markdown('<p style="color:#5A738A;font-size:13px;margin-top:-8px;">Visão consolidada de operações de prevenção à fraude</p>', unsafe_allow_html=True)
    with col2:
        src = ds.source
        dot = "🟢" if "Delta" in src else "🟡"
        st.markdown(f'<div style="text-align:right;padding-top:20px;font-size:12px;color:#5A738A;">{dot} {src}<br><span style="font-size:11px;">{datetime.now().strftime("%d/%m %H:%M")}</span></div>', unsafe_allow_html=True)

    with st.expander("🔍 Filtros Globais", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1: periodo = st.selectbox("Período", ["Hoje", "Últimos 7 dias", "Últimos 30 dias", "Últimos 45 dias"], index=2)
        with c2: f_status = st.multiselect("Status", STATUS_OPTIONS, default=[])
        with c3: f_priority = st.multiselect("Criticidade", PRIORITY_OPTIONS, default=[])
        with c4: f_fraud = st.multiselect("Tipo de Fraude", FRAUD_TYPES, default=[])
        c5, c6, c7, c8 = st.columns(4)
        with c5: f_channel = st.multiselect("Canal", CHANNELS, default=[])
        with c6: f_queue = st.multiselect("Fila", QUEUES, default=[])
        with c7:
            analysts = ds.get_analysts()
            f_analyst = st.multiselect("Analista", analysts["name"].tolist(), default=[])
        with c8: f_source = st.multiselect("Origem", ALERT_SOURCES, default=[])

    cases = ds.get_fraud_cases()
    now = datetime.now()
    days_map = {"Hoje": 1, "Últimos 7 dias": 7, "Últimos 30 dias": 30, "Últimos 45 dias": 45}
    cutoff = now - timedelta(days=days_map.get(periodo, 30))

    cases["created_at"] = pd.to_datetime(cases["created_at"])
    cases["sla_due_at"] = pd.to_datetime(cases["sla_due_at"])
    cases["closed_at"] = pd.to_datetime(cases.get("closed_at", pd.NaT))
    cases = cases[cases["created_at"] >= cutoff]

    if f_status:   cases = cases[cases["status"].isin(f_status)]
    if f_priority: cases = cases[cases["priority"].isin(f_priority)]
    if f_fraud:    cases = cases[cases["fraud_type"].isin(f_fraud)]
    if f_channel:  cases = cases[cases["channel"].isin(f_channel)]
    if f_queue:    cases = cases[cases["queue"].isin(f_queue)]
    if f_analyst:  cases = cases[cases["assigned_analyst"].isin(f_analyst)]
    if f_source:   cases = cases[cases["alert_source"].isin(f_source)]

    active = cases[cases["status"] != "Encerrado"]
    total      = len(cases)
    n_open     = len(active)
    n_critical = len(active[active["priority"] == "Crítica"])
    n_invest   = len(active[active["status"] == "Em Investigação"])
    n_docs     = len(active[active["status"] == "Aguardando Documentação"])
    n_closed   = len(cases[cases["status"] == "Encerrado"])
    n_escalado = len(active[active["status"] == "Escalado"])
    amount_risk = active["amount_at_risk"].sum()

    confirmed  = cases[cases["recommended_action"] == "Confirmar Fraude"]
    fraud_rate = len(confirmed) / total if total > 0 else 0

    closed_df = cases[(cases["status"] == "Encerrado") & cases["closed_at"].notna()]
    avg_h = ((closed_df["closed_at"] - closed_df["created_at"]).dt.total_seconds().mean() / 3600) if len(closed_df) > 0 else 0
    sla_vencido = len(active[active["sla_due_at"] < now])

    st.divider()
    cols = st.columns(6)
    kpis = [
        ("Casos Abertos",    str(n_open),                "📋", "#1565C0"),
        ("Casos Críticos",   str(n_critical),             "🚨", "#C62828"),
        ("Em Investigação",  str(n_invest),               "🔍", "#E65100"),
        ("Aguardando Docs",  str(n_docs),                 "📄", "#6A1B9A"),
        ("Encerrados",       str(n_closed),               "✅", "#2E7D32"),
        ("Valor em Risco",   format_currency(amount_risk), "💰", "#B71C1C"),
    ]
    for col, (title, val, icon, color) in zip(cols, kpis):
        with col:
            st.markdown(metric_card(title, val, icon, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Taxa Fraude Confirmada", format_percentage(fraud_rate))
    c2.metric("Tempo Médio Tratamento", f"{avg_h:.1f}h")
    c3.metric("SLA Vencido", str(sla_vencido))
    c4.metric("Escalados", str(n_escalado))
    c5.metric("Total no Período", str(total))
    st.divider()

    # Row 1
    col_l, col_r = st.columns(2)
    with col_l:
        sc = cases["status"].value_counts().reset_index()
        sc.columns = ["Status", "Quantidade"]
        fig = bar_chart(sc, x="Status", y="Quantidade", title="Backlog por Status",
                        color="Status", color_map=PALETTE_STATUS, height=340)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        ft = cases["fraud_type"].value_counts().reset_index()
        ft.columns = ["Tipo", "Quantidade"]
        fig = donut_chart(ft, names="Tipo", values="Quantidade",
                          title="Distribuição por Tipo de Fraude", height=340)
        st.plotly_chart(fig, use_container_width=True)

    # Row 2
    col_l, col_r = st.columns(2)
    with col_l:
        ch = cases["channel"].value_counts().reset_index()
        ch.columns = ["Canal", "Quantidade"]
        fig = bar_chart(ch, x="Canal", y="Quantidade", title="Casos por Canal", height=340)
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        tmp = cases.copy()
        tmp["Data"] = tmp["created_at"].dt.date
        daily = tmp.groupby("Data").size().reset_index(name="Casos")
        fig = area_chart(daily, x="Data", y="Casos", title="Evolução de Casos no Período", height=340)
        st.plotly_chart(fig, use_container_width=True)

    # Row 3
    col_l, col_r = st.columns(2)
    with col_l:
        order = ["Crítica", "Alta", "Média", "Baixa"]
        pc = active["priority"].value_counts().reindex(order, fill_value=0).reset_index()
        pc.columns = ["Prioridade", "Casos"]
        fig = bar_chart(pc, x="Prioridade", y="Casos", title="Casos Ativos por Prioridade",
                        color="Prioridade", color_map=PALETTE_PRIORITY, height=320)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    with col_r:
        ac = active[active["assigned_analyst"].notna()]["assigned_analyst"].value_counts().head(6).reset_index()
        ac.columns = ["Analista", "Casos"]
        fig = bar_chart(ac, x="Casos", y="Analista", orientation="h",
                        title="Carga por Analista (casos ativos)", height=320)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap
    st.markdown(f"<br>{section_header('💰 Valor em Risco por Tipo × Canal')}", unsafe_allow_html=True)
    pivot = active.pivot_table(values="amount_at_risk", index="fraud_type", columns="channel",
                               aggfunc="sum", fill_value=0)
    text_vals = [[f"R$ {v/1000:.0f}k" for v in row] for row in pivot.values]
    fig = heatmap(z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                  title="", height=380, text=text_vals)
    st.plotly_chart(fig, use_container_width=True)
