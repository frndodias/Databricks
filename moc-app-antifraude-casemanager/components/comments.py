import streamlit as st
import pandas as pd
from utils.formatting import format_datetime
from utils.constants import COMMENT_TYPES

_TYPE_COLORS = {
    "investigação": "#1565C0",
    "contato cliente": "#00838F",
    "evidência": "#6A1B9A",
    "decisão": "#C62828",
    "observação": "#F57C00",
}
_TYPE_ICONS = {
    "investigação": "🔍",
    "contato cliente": "📞",
    "evidência": "📎",
    "decisão": "⚖️",
    "observação": "📌",
}


def render_comments_section(case_id: str, comments_df: pd.DataFrame, case_service, current_user: str):
    st.markdown("#### 💬 Comentários do Analista")

    # --- Add comment form ---
    with st.expander("➕ Adicionar Comentário", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            comment_text = st.text_area("Comentário", height=100, placeholder="Descreva sua análise, evidência ou decisão...", key=f"comment_text_{case_id}")
        with col2:
            comment_type = st.selectbox("Categoria", COMMENT_TYPES, key=f"comment_type_{case_id}")
            important = st.checkbox("Marcar como importante", key=f"comment_imp_{case_id}")

        if st.button("💾 Salvar Comentário", key=f"save_comment_{case_id}", type="primary"):
            if comment_text.strip():
                case_service.add_comment(case_id, current_user, comment_type, comment_text.strip(), important)
                st.success("Comentário adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Digite o texto do comentário antes de salvar.")

    # --- Comment list ---
    if comments_df.empty:
        st.info("Nenhum comentário registrado.")
        return

    # Sort: important first, then by date desc
    df = comments_df.copy()
    df["sort_key"] = df["important_flag"].astype(int)
    df = df.sort_values(["sort_key", "created_at"], ascending=[False, False])

    for _, row in df.iterrows():
        ctype = str(row.get("comment_type", "observação"))
        color = _TYPE_COLORS.get(ctype, "#666")
        icon = _TYPE_ICONS.get(ctype, "💬")
        is_important = row.get("important_flag", False)
        border_color = "#D32F2F" if is_important else color

        important_badge = '<span style="background:#FFEBEE;color:#C62828;border-radius:8px;padding:2px 8px;font-size:10px;font-weight:700;margin-left:8px;">⭐ IMPORTANTE</span>' if is_important else ""

        st.markdown(f"""
<div style="background:#fff;border:1px solid #E0E4EB;border-left:4px solid {border_color};
            border-radius:0 10px 10px 0;padding:14px 16px;margin-bottom:10px;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="background:{color}22;color:{color};border:1px solid {color};border-radius:12px;
                   padding:2px 10px;font-size:11px;font-weight:600;">{icon} {ctype.title()}</span>
      {important_badge}
    </div>
    <span style="font-size:11px;color:#9E9E9E;">{format_datetime(row.get('created_at'))}</span>
  </div>
  <div style="font-size:13px;color:#333;line-height:1.6;margin-bottom:8px;">{row.get('comment_text','')}</div>
  <div style="font-size:11px;color:#9E9E9E;">por <strong style="color:#555;">{row.get('author','')}</strong></div>
</div>
""", unsafe_allow_html=True)
