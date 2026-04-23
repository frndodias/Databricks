import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.data_service import DataService
from views.dashboard import render_dashboard
from views.case_queue import render_case_queue
from views.case_detail import render_case_detail
from views.management import render_management
from components.styles import inject_styles

st.set_page_config(
    page_title="Anti-Fraude | Case Manager",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# ── Session state defaults ────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "selected_case_id" not in st.session_state:
    st.session_state.selected_case_id = None
if "current_user" not in st.session_state:
    st.session_state.current_user = "Ana Souza"


@st.cache_resource(show_spinner="Carregando dados...")
def get_data_service():
    return DataService()


ds = get_data_service()

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:20px 0 12px;">'
        '<div style="font-size:40px;">🛡️</div>'
        '<div style="font-size:18px;font-weight:800;color:#E8EDF5;margin-top:6px;letter-spacing:0.5px;">Anti-Fraude</div>'
        '<div style="font-size:11px;color:#6B83B0;margin-top:3px;letter-spacing:1px;text-transform:uppercase;">Case Manager Enterprise</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.divider()

    analysts_df = ds.get_analysts()
    analyst_names = analysts_df["name"].tolist()
    current_user = st.selectbox(
        "👤 Usuário logado",
        analyst_names,
        index=analyst_names.index(st.session_state.current_user) if st.session_state.current_user in analyst_names else 0,
        key="user_selector",
    )
    st.session_state.current_user = current_user

    st.divider()

    nav_items = [
        ("dashboard",  "📊  Dashboard Executivo"),
        ("queue",      "📋  Fila de Casos"),
        ("management", "📈  Gestão Operacional"),
    ]

    for page_id, label in nav_items:
        is_active = st.session_state.page == page_id
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, use_container_width=True, key=f"nav_{page_id}", type=btn_type):
            st.session_state.page = page_id
            st.session_state.selected_case_id = None
            st.rerun()

    st.divider()

    import pandas as pd
    try:
        cases = ds.get_fraud_cases()
        active = cases[cases["status"] != "Encerrado"].copy()
        n_open = len(active)
        n_critical = len(active[active["priority"] == "Crítica"])
        n_sla = len(active[pd.to_datetime(active["sla_due_at"]) < pd.Timestamp.now()])

        st.markdown(
            '<div style="font-size:10px;color:#6B83B0;font-weight:700;text-transform:uppercase;'
            'letter-spacing:1px;margin-bottom:10px;">Status Atual</div>',
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        col1.metric("Ativos", n_open)
        col2.metric("🚨 Críticos", n_critical)
        st.metric("⏰ SLA Vencido", n_sla)
    except Exception:
        pass

    st.divider()

    src = ds.source
    color = "#4CAF50" if "Delta" in src else "#FF9800"
    dot = "🟢" if "Delta" in src else "🟡"
    st.markdown(
        f'<div style="font-size:11px;color:{color};text-align:center;padding:4px 0;">'
        f'{dot} {src}</div>',
        unsafe_allow_html=True,
    )

# ── Page routing ──────────────────────────────────────────────────────
if st.session_state.page == "dashboard":
    render_dashboard(ds)
elif st.session_state.page == "queue":
    if st.session_state.selected_case_id:
        render_case_detail(ds, st.session_state.selected_case_id)
    else:
        render_case_queue(ds)
elif st.session_state.page == "management":
    render_management(ds)
