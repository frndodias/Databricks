import streamlit as st
import pandas as pd
from datetime import datetime
from utils.formatting import (
    format_currency, format_datetime, format_aging,
    get_status_badge, get_priority_badge, get_action_badge,
    get_score_color, is_sla_overdue,
)
from utils.constants import STATUS_OPTIONS, PRIORITY_OPTIONS, SEVERITY_OPTIONS, FRAUD_TYPES, CHANNELS, QUEUES


def render_case_queue(ds):
    st.title("📋 Fila de Casos")
    st.markdown("*Gerencie e priorize os casos da fila operacional*")

    cases = ds.get_fraud_cases()
    analysts = ds.get_analysts()
    analyst_names = analysts["name"].tolist()

    cases["created_at"] = pd.to_datetime(cases["created_at"])
    cases["sla_due_at"] = pd.to_datetime(cases["sla_due_at"])

    # ── Search ────────────────────────────────────────────────────────
    search = st.text_input(
        "🔎 Buscar",
        placeholder="Busque por case_id, customer_id, transaction_id, device_id, nome ou documento...",
        key="queue_search",
    )
    if search:
        s = search.lower()
        mask = (
            cases["case_id"].str.lower().str.contains(s, na=False) |
            cases["customer_id"].str.lower().str.contains(s, na=False) |
            cases["transaction_id"].str.lower().str.contains(s, na=False) |
            cases["device_id"].str.lower().str.contains(s, na=False)
        )
        cases = cases[mask]

    # ── Filters ───────────────────────────────────────────────────────
    with st.expander("⚙️ Filtros e Ordenação", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_status = st.multiselect("Status", STATUS_OPTIONS, default=[], key="q_status")
        with c2:
            f_priority = st.multiselect("Prioridade", PRIORITY_OPTIONS, default=[], key="q_priority")
        with c3:
            f_fraud = st.multiselect("Tipo Fraude", FRAUD_TYPES, default=[], key="q_fraud")
        with c4:
            f_channel = st.multiselect("Canal", CHANNELS, default=[], key="q_channel")

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            f_queue = st.multiselect("Fila", QUEUES, default=[], key="q_queue")
        with c6:
            f_analyst = st.multiselect("Analista", ["Não atribuído"] + analyst_names, default=[], key="q_analyst")
        with c7:
            score_min = st.slider("Score Mínimo", 0, 999, 0, key="q_score")
        with c8:
            sort_by = st.selectbox("Ordenar por", ["Score (maior primeiro)", "Valor (maior primeiro)", "SLA (mais urgente)", "Data (mais recente)", "Data (mais antigo)"], key="q_sort")

    # Apply filters
    if f_status:    cases = cases[cases["status"].isin(f_status)]
    if f_priority:  cases = cases[cases["priority"].isin(f_priority)]
    if f_fraud:     cases = cases[cases["fraud_type"].isin(f_fraud)]
    if f_channel:   cases = cases[cases["channel"].isin(f_channel)]
    if f_queue:     cases = cases[cases["queue"].isin(f_queue)]
    if "Não atribuído" in f_analyst:
        cases = cases[cases["assigned_analyst"].isna()]
    elif f_analyst:
        cases = cases[cases["assigned_analyst"].isin(f_analyst)]
    cases = cases[cases["risk_score"] >= score_min]

    # Apply sort
    sort_map = {
        "Score (maior primeiro)":   ("risk_score", False),
        "Valor (maior primeiro)":   ("amount_at_risk", False),
        "SLA (mais urgente)":       ("sla_due_at", True),
        "Data (mais recente)":      ("created_at", False),
        "Data (mais antigo)":       ("created_at", True),
    }
    sort_col, asc = sort_map[sort_by]
    cases = cases.sort_values(sort_col, ascending=asc)

    # ── Summary ───────────────────────────────────────────────────────
    now = datetime.now()
    total = len(cases)
    n_sla = len(cases[cases["sla_due_at"] < now])
    n_critical = len(cases[cases["priority"] == "Crítica"])

    c1, c2, c3 = st.columns(3)
    c1.metric("Casos na Fila", total)
    c2.metric("SLA Vencido", n_sla, delta=None)
    c3.metric("Críticos", n_critical, delta=None)

    st.divider()

    if cases.empty:
        st.info("Nenhum caso encontrado com os filtros aplicados.")
        return

    # ── Case Table ────────────────────────────────────────────────────
    st.markdown(f"**{total} casos encontrados**")

    for _, row in cases.iterrows():
        _render_case_row(row, now)


def _render_case_row(row, now):
    case_id = row["case_id"]
    sla_overdue = row.get("sla_due_at", now) < now and row.get("status") != "Encerrado"
    border_color = "#D32F2F" if sla_overdue else ("#FF6F00" if row["priority"] == "Crítica" else "#E0E4EB")
    bg = "#FFF8F8" if sla_overdue else "#FFFFFF"
    score = int(row.get("risk_score", 0))
    sc = get_score_color(score)

    aging = format_aging(row.get("created_at"))
    sla_label = "⏰ SLA VENCIDO" if sla_overdue else f"SLA: {format_datetime(row.get('sla_due_at'))}"
    analyst = row.get("assigned_analyst") or "Não atribuído"

    header_html = f"""
<div style="background:{bg};border:1px solid {border_color};border-radius:10px;padding:14px 18px;
            margin-bottom:10px;{'border-left:4px solid #D32F2F;' if sla_overdue else ''}">
  <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
      <span style="font-size:14px;font-weight:800;color:#1565C0;">{case_id}</span>
      {get_priority_badge(row.get('priority',''))}
      {get_status_badge(row.get('status',''))}
      {get_action_badge(row.get('recommended_action',''))}
      {'<span style="background:#D32F2F;color:#fff;border-radius:8px;padding:2px 8px;font-size:11px;font-weight:700;">⏰ SLA VENCIDO</span>' if sla_overdue else ''}
    </div>
    <div style="text-align:right;">
      <div style="font-size:11px;color:#9E9E9E;">{format_datetime(row.get('created_at'))} · {aging}</div>
      <div style="font-size:11px;color:{'#D32F2F' if sla_overdue else '#9E9E9E'};font-weight:{'700' if sla_overdue else '400'};">{sla_label}</div>
    </div>
  </div>
  <div style="display:flex;gap:24px;flex-wrap:wrap;align-items:center;">
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Score</span>
      <div style="font-size:20px;font-weight:800;color:{sc};">{score}</div>
    </div>
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Valor em Risco</span>
      <div style="font-size:14px;font-weight:700;color:#333;">{format_currency(row.get('amount_at_risk',0))}</div>
    </div>
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Tipo</span>
      <div style="font-size:13px;color:#333;">{row.get('fraud_type','')}</div>
    </div>
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Canal</span>
      <div style="font-size:13px;color:#333;">{row.get('channel','')}</div>
    </div>
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Analista</span>
      <div style="font-size:13px;color:{'#9E9E9E' if analyst == 'Não atribuído' else '#333'};font-style:{'italic' if analyst == 'Não atribuído' else 'normal'};">{analyst}</div>
    </div>
    <div>
      <span style="font-size:11px;color:#9E9E9E;">Fila</span>
      <div style="font-size:13px;color:#333;">{row.get('queue','')}</div>
    </div>
  </div>
</div>
"""
    st.markdown(header_html, unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        if st.button(f"Abrir Caso →", key=f"open_{case_id}", use_container_width=True):
            st.session_state.selected_case_id = case_id
            st.session_state.page = "queue"
            st.rerun()
