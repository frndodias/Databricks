import streamlit as st
from services.heuristics import apply_risk_rules

_ACTION_ICONS = {
    "Bloquear Preventivamente": ("🚫", "#D32F2F", "#FFEBEE"),
    "Confirmar Fraude":         ("🔴", "#B71C1C", "#FFCDD2"),
    "Revisar Manualmente":      ("🔍", "#F57C00", "#FFF3E0"),
    "Aprovar":                  ("✅", "#2E7D32", "#E8F5E9"),
}


def render_ai_assistant(case: dict, customer: dict, transaction: dict, device: dict):
    st.markdown("#### 🤖 Assistente de Investigação")
    st.markdown(
        '<div style="background:linear-gradient(135deg,#E8EDF8,#F0F4FF);border:1px solid #C5D0E8;'
        'border-radius:10px;padding:4px 12px;margin-bottom:12px;">'
        '<span style="font-size:11px;color:#4A5568;">Análise heurística automatizada — '
        'arquitetura pronta para integração com LLM/Modelos ML</span></div>',
        unsafe_allow_html=True,
    )

    analysis = apply_risk_rules(case, customer, transaction, device)
    action = analysis["recommended_action"]
    icon, color, bg = _ACTION_ICONS.get(action, ("⚪", "#666", "#F5F5F5"))

    # --- Summary ---
    st.markdown(
        f'<div style="background:#F8F9FC;border:1px solid #E0E4EB;border-radius:8px;padding:14px;'
        f'margin-bottom:14px;font-size:13px;line-height:1.7;color:#333;">{analysis["summary"]}</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        # Recommendation box
        st.markdown(
            f'<div style="background:{bg};border:2px solid {color};border-radius:10px;'
            f'padding:16px;text-align:center;margin-bottom:14px;">'
            f'<div style="font-size:28px;">{icon}</div>'
            f'<div style="font-size:11px;color:#666;margin-top:4px;font-weight:600;">RECOMENDAÇÃO</div>'
            f'<div style="font-size:18px;font-weight:800;color:{color};margin-top:4px;">{action}</div>'
            f'<div style="font-size:12px;color:{color}99;margin-top:6px;">Confiança: {analysis["confidence"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Risk factors
        if analysis["aggravating"]:
            st.markdown("**🔴 Principais fatores de risco:**")
            for f in analysis["aggravating"]:
                st.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:8px;padding:4px 0;">'
                    f'<span style="color:#D32F2F;font-size:16px;line-height:1;">▲</span>'
                    f'<span style="font-size:13px;color:#333;">{f}</span></div>',
                    unsafe_allow_html=True,
                )

    with col2:
        # Legitimacy factors
        if analysis["mitigating"]:
            st.markdown("**🟢 Fatores que indicam legitimidade:**")
            for f in analysis["mitigating"]:
                st.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:8px;padding:4px 0;">'
                    f'<span style="color:#388E3C;font-size:16px;line-height:1;">▼</span>'
                    f'<span style="font-size:13px;color:#333;">{f}</span></div>',
                    unsafe_allow_html=True,
                )

        # Rules triggered
        if analysis["rules_triggered"]:
            st.markdown("**⚠️ Regras/Modelos disparados:**")
            for r in analysis["rules_triggered"]:
                sev_color = {"Crítica": "#D32F2F", "Alta": "#F57C00", "Média": "#F9A825", "Baixa": "#388E3C"}.get(r.get("severity", ""), "#666")
                st.markdown(
                    f'<div style="background:{sev_color}11;border:1px solid {sev_color}33;border-radius:6px;'
                    f'padding:6px 10px;margin-bottom:4px;">'
                    f'<span style="font-size:11px;font-weight:700;color:{sev_color};">{r["rule"]}</span>'
                    f'<div style="font-size:11px;color:#555;margin-top:2px;">{r["description"]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

    # Next steps
    st.markdown("**📋 Próximos Passos Sugeridos:**")
    for i, step in enumerate(analysis["next_steps"], 1):
        st.markdown(
            f'<div style="display:flex;gap:10px;padding:6px 0;border-bottom:1px solid #F0F0F0;">'
            f'<span style="background:#1565C0;color:#fff;border-radius:50%;width:20px;height:20px;'
            f'display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;'
            f'flex-shrink:0;">{i}</span>'
            f'<span style="font-size:13px;color:#333;line-height:1.5;">{step}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
