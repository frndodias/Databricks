import streamlit as st
import pandas as pd
from utils.formatting import format_datetime

_ICON_MAP = {
    "Criação": ("🔵", "#1565C0"),
    "Mudança de Status": ("🔄", "#F57C00"),
    "Atribuição": ("👤", "#6A1B9A"),
    "Comentário": ("💬", "#00838F"),
    "Bloqueio": ("🚫", "#D32F2F"),
    "Escalamento": ("⬆️", "#C62828"),
    "Decisão": ("⚖️", "#1B5E20"),
    "Revisão": ("🔍", "#0277BD"),
    "Solicitação Documentação": ("📄", "#4527A0"),
    "default": ("⚪", "#9E9E9E"),
}


def render_timeline(history_df: pd.DataFrame):
    st.markdown("#### 📋 Linha do Tempo do Caso")
    if history_df.empty:
        st.info("Nenhum registro de histórico encontrado.")
        return

    history_sorted = history_df.sort_values("action_timestamp", ascending=False)

    for _, row in history_sorted.iterrows():
        action = str(row.get("action_type", ""))
        icon, color = _ICON_MAP.get(action, _ICON_MAP["default"])
        ts = format_datetime(row.get("action_timestamp"))
        by = row.get("action_by", "Sistema")
        old_val = row.get("old_value")
        new_val = row.get("new_value")

        change_text = ""
        if old_val and new_val and str(old_val) != "None":
            change_text = f'<span style="color:#888;text-decoration:line-through;">{old_val}</span> → <strong>{new_val}</strong>'
        elif new_val and str(new_val) != "None":
            change_text = f'<strong>{new_val}</strong>'

        st.markdown(f"""
<div style="display:flex;gap:16px;padding:12px 0;border-bottom:1px solid #F0F4F8;align-items:flex-start;">
  <div style="display:flex;flex-direction:column;align-items:center;gap:4px;min-width:24px;">
    <div style="width:24px;height:24px;border-radius:50%;background:{color}22;
                border:2px solid {color};display:flex;align-items:center;justify-content:center;
                font-size:12px;line-height:1;">{icon}</div>
    <div style="width:2px;flex:1;background:{color}33;min-height:16px;"></div>
  </div>
  <div style="flex:1;padding-bottom:4px;">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
      <span style="font-weight:600;font-size:13px;color:#1A1A2E;">{action}</span>
      <span style="font-size:11px;color:#9E9E9E;">{ts}</span>
    </div>
    <div style="font-size:12px;color:#555;margin-bottom:2px;">{change_text}</div>
    <div style="font-size:11px;color:#9E9E9E;">por <strong style="color:#555;">{by}</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)
