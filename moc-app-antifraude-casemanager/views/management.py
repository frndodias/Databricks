import streamlit as st
import pandas as pd
from datetime import datetime
from utils.formatting import format_currency, format_percentage
from utils.charts import bar_chart, heatmap, PALETTE_PRIORITY
from components.styles import metric_card, section_header


def render_management(ds):
    st.title("📈 Gestão Operacional")
    st.markdown('<p style="color:#5A738A;font-size:13px;margin-top:-8px;">Indicadores de produtividade, SLA e eficiência da equipe</p>', unsafe_allow_html=True)

    cases = ds.get_fraud_cases()
    cases["created_at"] = pd.to_datetime(cases["created_at"])
    cases["sla_due_at"] = pd.to_datetime(cases["sla_due_at"])
    now = datetime.now()

    active = cases[cases["status"] != "Encerrado"]
    closed = cases[cases["status"] == "Encerrado"]

    st.divider()
    cols = st.columns(5)
    total_closed = len(closed)
    confirmed_fraud = len(cases[cases["recommended_action"] == "Confirmar Fraude"])
    total_risk = cases["amount_at_risk"].sum()
    confirmed_risk = cases[cases["recommended_action"] == "Confirmar Fraude"]["amount_at_risk"].sum()
    avoided = total_risk - confirmed_risk

    kpis = [
        ("Casos Encerrados",    str(total_closed), "✅", "#2E7D32"),
        ("Fraude Confirmada",   str(confirmed_fraud), "🔴", "#C62828"),
        ("Taxa de Confirmação", format_percentage(confirmed_fraud / len(cases) if len(cases) > 0 else 0), "📊", "#E65100"),
        ("Perdas Evitadas Est.", format_currency(avoided), "💰", "#1565C0"),
        ("SLA Vencido (ativos)", str(len(active[active["sla_due_at"] < now])), "⏰", "#B71C1C"),
    ]
    for col, (title, val, icon, color) in zip(cols, kpis):
        with col:
            st.markdown(metric_card(title, val, icon, color), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Analyst productivity ──────────────────────────────────────────
    st.markdown(section_header("👥 Produtividade por Analista"), unsafe_allow_html=True)
    if cases[cases["assigned_analyst"].notna()].shape[0] > 0:
        stats = (
            cases[cases["assigned_analyst"].notna()]
            .groupby("assigned_analyst")
            .agg(
                Total=("case_id", "count"),
                Ativos=("status", lambda x: (x != "Encerrado").sum()),
                Encerrados=("status", lambda x: (x == "Encerrado").sum()),
                Críticos=("priority", lambda x: (x == "Crítica").sum()),
            )
            .reset_index()
            .rename(columns={"assigned_analyst": "Analista"})
        )
        stats["Encerr. (%)"] = (stats["Encerrados"] / stats["Total"] * 100).round(1)

        col_t, col_c = st.columns([1, 1])
        with col_t:
            st.dataframe(stats, use_container_width=True, hide_index=True)
        with col_c:
            fig = bar_chart(stats, x="Analista", y=["Ativos", "Encerrados"],
                            title="Volume por Analista", height=320, barmode="stack",
                            color_map={"Ativos": "#F57C00", "Encerrados": "#388E3C"})
            fig.update_layout(showlegend=True,
                              legend=dict(font=dict(color="#0D1B2A", size=11)))
            st.plotly_chart(fig, use_container_width=True)

    # ── Queue backlog ─────────────────────────────────────────────────
    st.markdown(section_header("📥 Backlog por Fila"), unsafe_allow_html=True)
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        qs = active.groupby(["queue", "priority"]).size().reset_index(name="Casos")
        fig = bar_chart(qs, x="queue", y="Casos", title="Backlog por Fila e Prioridade",
                        color="priority", color_map=PALETTE_PRIORITY, barmode="stack", height=320)
        fig.update_layout(xaxis_title="Fila", showlegend=True,
                          legend=dict(font=dict(color="#0D1B2A", size=11), title_text="Prioridade"))
        st.plotly_chart(fig, use_container_width=True)
    with col_q2:
        qsum = active.groupby("queue").agg(Casos=("case_id","count"), Valor=("amount_at_risk","sum")).reset_index()
        qsum.columns = ["Fila", "Casos", "Valor em Risco (R$)"]
        qsum["Valor em Risco (R$)"] = qsum["Valor em Risco (R$)"].apply(lambda v: f"R$ {v:,.0f}".replace(",","."))
        st.dataframe(qsum, use_container_width=True, hide_index=True)

    # ── SLA analysis ──────────────────────────────────────────────────
    st.markdown(section_header("⏰ SLA por Severidade"), unsafe_allow_html=True)
    sla_rows = []
    for sev in ["Crítica", "Alta", "Média", "Baixa"]:
        s = active[active["severity"] == sev]
        total_s = len(s)
        overdue_s = len(s[s["sla_due_at"] < now])
        sla_rows.append({"Severidade": sev, "Dentro do SLA": total_s - overdue_s,
                         "SLA Vencido": overdue_s,
                         "Adimplência": f"{(1-overdue_s/total_s)*100:.0f}%" if total_s else "N/A"})
    sla_df = pd.DataFrame(sla_rows)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.dataframe(sla_df, use_container_width=True, hide_index=True)
    with col_s2:
        fig = bar_chart(sla_df, x="Severidade", y=["Dentro do SLA", "SLA Vencido"],
                        title="Adimplência de SLA por Severidade", barmode="group", height=280,
                        color_map={"Dentro do SLA": "#2E7D32", "SLA Vencido": "#C62828"})
        fig.update_layout(showlegend=True, legend=dict(font=dict(color="#0D1B2A", size=11)))
        st.plotly_chart(fig, use_container_width=True)

    # ── Aging ─────────────────────────────────────────────────────────
    st.markdown(section_header("📅 Aging por Status"), unsafe_allow_html=True)
    aging_rows = []
    for status in ["Aberto", "Em Investigação", "Aguardando Documentação", "Escalado"]:
        s = active[active["status"] == status]
        if len(s) > 0:
            ages = (now - s["created_at"]).dt.total_seconds() / 3600
            aging_rows.append({"Status": status, "Casos": len(s),
                               "Aging Médio (h)": round(ages.mean(), 1),
                               "Aging Máx. (h)": round(ages.max(), 1)})
    if aging_rows:
        aging_df = pd.DataFrame(aging_rows)
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            st.dataframe(aging_df, use_container_width=True, hide_index=True)
        with col_a2:
            sc_map = {"Aberto": "#1976D2", "Em Investigação": "#F57C00",
                      "Aguardando Documentação": "#7B1FA2", "Escalado": "#C62828"}
            fig = bar_chart(aging_df, x="Status", y="Aging Médio (h)",
                            title="Aging Médio por Status (horas)",
                            color="Status", color_map=sc_map, height=280)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # ── Fraud heatmap ─────────────────────────────────────────────────
    st.markdown(section_header("🌡️ Fraudes Confirmadas: Canal × Tipo"), unsafe_allow_html=True)
    conf = cases[cases["recommended_action"].isin(["Confirmar Fraude", "Bloquear Preventivamente"])]
    if not conf.empty:
        pivot = conf.pivot_table(values="amount_at_risk", index="fraud_type",
                                 columns="channel", aggfunc="count", fill_value=0)
        fig = heatmap(z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
                      title="", height=380, text=[[str(int(v)) for v in row] for row in pivot.values])
        st.plotly_chart(fig, use_container_width=True)
