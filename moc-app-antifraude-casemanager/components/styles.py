import streamlit as st


def inject_styles():
    st.markdown("""
<style>
/* ============================================================
   Anti-Fraude Case Manager — Global Styles
   ============================================================ */

/* Hide ALL Streamlit default chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
.st-emotion-cache-16idsys { display: none !important; }
section[data-testid="stSidebarNav"] { display: none !important; }

/* Tighten top padding */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 100% !important;
}

/* ── Main content — all labels/text DARK ─────────────── */
.main label,
.main p,
.main span,
.main [data-testid="stWidgetLabel"],
.main [data-testid="stWidgetLabel"] p,
[data-testid="stMain"] label,
[data-testid="stMain"] p,
[data-testid="stMain"] [data-testid="stWidgetLabel"],
[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
[data-testid="stExpander"] label,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] [data-testid="stWidgetLabel"] p {
    color: #1A2E4A !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A1628 0%, #0F1E35 50%, #0A1628 100%) !important;
    border-right: 1px solid #1E3050 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
/* All text in sidebar — scoped tightly so it doesn't leak */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    color: #C8D8F0 !important;
}
/* Sidebar selectbox */
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #1A2E4A !important;
    border-color: #2A4A70 !important;
    color: #E0ECFF !important;
}
/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: #C8D8F0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 14px !important;
    text-align: left !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.25) !important;
    color: #FFFFFF !important;
}
/* Active nav button (primary) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1565C0, #1976D2) !important;
    border-color: #1E88E5 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}
/* Sidebar metrics */
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #E0ECFF !important;
    font-size: 20px !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #6B83B0 !important;
    font-size: 11px !important;
}
/* Sidebar divider */
[data-testid="stSidebar"] hr {
    border-color: #1E3050 !important;
    margin: 12px 0 !important;
}

/* ── Main content area ───────────────────────────────── */
.stApp {
    background-color: #F3F6FB !important;
}

/* ── Page title ──────────────────────────────────────── */
h1 {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #0D1B2A !important;
    margin-bottom: 2px !important;
}
h2 {
    font-size: 20px !important;
    font-weight: 700 !important;
    color: #0D1B2A !important;
}
h3, h4 {
    color: #1A2E4A !important;
    font-weight: 700 !important;
}

/* ── Cards ───────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E0E8F4;
    border-radius: 10px;
    padding: 14px 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
[data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #0D1B2A !important;
}
[data-testid="stMetricLabel"] {
    font-size: 12px !important;
    color: #5A738A !important;
    font-weight: 600 !important;
}

/* ── Tabs ────────────────────────────────────────────── */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid #E0E8F4 !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    color: #5A738A !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 18px !important;
    margin-bottom: -2px !important;
}
[data-baseweb="tab"]:hover {
    background: #EDF2FB !important;
    color: #1565C0 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    border-bottom: 3px solid #1565C0 !important;
    color: #1565C0 !important;
    background: transparent !important;
}
[data-baseweb="tab-panel"] {
    padding: 20px 0 0 !important;
}

/* ── Buttons — main content ──────────────────────────── */
.main .stButton > button,
[data-testid="stMain"] .stButton > button {
    background: #FFFFFF !important;
    color: #1A2E4A !important;
    border: 1px solid #C8D8F0 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
.main .stButton > button:hover,
[data-testid="stMain"] .stButton > button:hover {
    background: #F0F5FF !important;
    border-color: #1565C0 !important;
    color: #1565C0 !important;
    box-shadow: 0 2px 8px rgba(21,101,192,0.15) !important;
}
.main .stButton > button[kind="primary"],
[data-testid="stMain"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1565C0, #1976D2) !important;
    border-color: #1565C0 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 6px rgba(21,101,192,0.3) !important;
}
.main .stButton > button[kind="primary"]:hover,
[data-testid="stMain"] .stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 12px rgba(21,101,192,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Expander ────────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E0E8F4 !important;
    border-radius: 10px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    color: #1A2E4A !important;
    font-size: 13px !important;
}

/* ── Dataframe ───────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    border: 1px solid #E0E8F4 !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
}

/* ── Inputs / selects ────────────────────────────────── */
[data-baseweb="input"], [data-baseweb="select"] > div,
[data-baseweb="textarea"] {
    border-radius: 8px !important;
    border-color: #C8D8F0 !important;
    background: #FFFFFF !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: #1565C0 !important;
    box-shadow: 0 0 0 2px rgba(21,101,192,0.15) !important;
}

/* ── Alert boxes ─────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* ── Divider ─────────────────────────────────────────── */
hr {
    border-color: #E0E8F4 !important;
    margin: 16px 0 !important;
}

/* ── Plotly chart containers ─────────────────────────── */
.js-plotly-plot {
    border-radius: 10px;
}

/* ── Popover — mesmo padrão dos botões brancos ───────── */
[data-testid="stPopover"] > button,
[data-testid="stPopover"] button[data-testid="stBaseButton-secondary"] {
    background: #FFFFFF !important;
    color: #1A2E4A !important;
    border: 1px solid #C8D8F0 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    outline: none !important;
}
[data-testid="stPopover"] > button:hover {
    background: #F0F5FF !important;
    border-color: #1565C0 !important;
    color: #1565C0 !important;
}
</style>
""", unsafe_allow_html=True)


def metric_card(title: str, value: str, icon: str, color: str, subtitle: str = "") -> str:
    sub = f'<div style="font-size:11px;color:{color}BB;margin-top:4px;font-weight:500;">{subtitle}</div>' if subtitle else ""
    return f"""
<div style="background:#FFFFFF;border-radius:12px;padding:20px 16px;
            box-shadow:0 2px 8px rgba(0,0,0,0.06);border:1px solid #E0E8F4;
            border-top:4px solid {color};text-align:center;height:100%;">
  <div style="font-size:28px;margin-bottom:8px;line-height:1;">{icon}</div>
  <div style="font-size:26px;font-weight:900;color:{color};line-height:1.1;letter-spacing:-0.5px;">{value}</div>
  <div style="font-size:11px;color:#5A738A;margin-top:8px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">{title}</div>
  {sub}
</div>"""


def section_header(title: str, color: str = "#1565C0") -> str:
    return f"""
<div style="font-size:13px;font-weight:700;color:{color};padding:8px 0 6px;
            border-bottom:2px solid {color}33;margin-bottom:12px;
            letter-spacing:0.3px;text-transform:uppercase;">
  {title}
</div>"""


def info_row(label: str, value: str, bold: bool = False) -> str:
    weight = "700" if bold else "400"
    color = "#0D1B2A" if bold else "#374151"
    return f"""
<div style="display:flex;justify-content:space-between;align-items:center;
            padding:7px 0;border-bottom:1px solid #F0F4FB;">
  <span style="color:#6B7280;font-size:12px;font-weight:500;">{label}</span>
  <span style="color:{color};font-size:13px;font-weight:{weight};text-align:right;max-width:60%;">{value}</span>
</div>"""
