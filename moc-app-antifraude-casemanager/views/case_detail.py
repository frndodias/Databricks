import streamlit as st
import pandas as pd
from datetime import datetime
from utils.formatting import (
    format_currency, format_datetime, format_aging,
    get_status_badge, get_priority_badge, get_action_badge, get_score_color,
)
from utils.constants import STATUS_OPTIONS, QUEUES
from components.styles import metric_card, section_header, info_row
from components.timeline import render_timeline
from components.comments import render_comments_section
from components.ai_assistant import render_ai_assistant
from services.case_service import CaseService


def render_case_detail(ds, case_id: str):
    case = ds.get_case(case_id)
    if not case:
        st.error(f"Caso {case_id} não encontrado.")
        return

    cs = CaseService(ds)
    current_user = st.session_state.get("current_user", "Analista")

    # ── Back button ───────────────────────────────────────────────────
    if st.button("← Voltar para a Fila", key="back_to_queue"):
        st.session_state.selected_case_id = None
        st.rerun()

    st.divider()

    # ── Case header ───────────────────────────────────────────────────
    score = int(case.get("risk_score", 0))
    sc = get_score_color(score)
    sla_due = pd.to_datetime(case.get("sla_due_at"))
    sla_overdue = datetime.now() > sla_due and case.get("status") != "Encerrado"

    col_title, col_score = st.columns([5, 1])
    with col_title:
        st.markdown(f"## 🛡️ Caso {case_id}")
        badges = f"{get_priority_badge(case.get('priority',''))} &nbsp; {get_status_badge(case.get('status',''))} &nbsp; {get_action_badge(case.get('recommended_action',''))}"
        if sla_overdue:
            badges += ' &nbsp; <span style="background:#D32F2F;color:#fff;border-radius:8px;padding:3px 10px;font-size:11px;font-weight:700;">⏰ SLA VENCIDO</span>'
        st.markdown(badges, unsafe_allow_html=True)
    with col_score:
        risk_cls = "risk-critical" if score > 900 else ("risk-high" if score > 750 else ("risk-medium" if score > 600 else "risk-low"))
        st.markdown(
            f'<div style="text-align:center;padding:10px;">'
            f'<div style="font-size:11px;color:#888;font-weight:600;text-transform:uppercase;">Score de Risco</div>'
            f'<div class="risk-score {risk_cls}" style="font-size:32px;font-weight:900;color:{sc};">{score}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Quick actions ─────────────────────────────────────────────────
    st.markdown("**⚡ Ações Rápidas**")
    ac1, ac2, ac3, ac4, ac5, ac6, ac7, ac8 = st.columns(8)

    with ac1:
        if st.button("👤 Atribuir p/ mim", key="assign_me", use_container_width=True):
            cs.assign_to_me(case_id, current_user)
            st.success(f"Caso atribuído para {current_user}")
            st.rerun()
    with ac2:
        if st.button("✅ Confirmar Fraude", key="confirm_fraud", use_container_width=True):
            cs.confirm_fraud(case_id, current_user)
            st.success("Caso marcado como Fraude Confirmada")
            st.rerun()
    with ac3:
        if st.button("🟢 Falso Positivo", key="false_pos", use_container_width=True):
            cs.mark_false_positive(case_id, current_user)
            st.success("Caso marcado como Falso Positivo")
            st.rerun()
    with ac4:
        if st.button("🚫 Bloquear", key="block_btn", use_container_width=True):
            cs.block_preventive(case_id, current_user)
            st.success("Bloqueio preventivo aplicado")
            st.rerun()
    with ac5:
        if st.button("⬆️ Escalar", key="escalate_btn", use_container_width=True):
            cs.escalate(case_id, current_user)
            st.success("Caso escalado para Alta Complexidade")
            st.rerun()
    with ac6:
        if st.button("📄 Solicitar Docs", key="req_docs", use_container_width=True):
            cs.request_docs(case_id, current_user)
            st.success("Documentação solicitada")
            st.rerun()
    with ac7:
        if st.button("🔍 Solicitar Revisão", key="req_review", use_container_width=True):
            cs.request_review(case_id, current_user)
            st.success("Revisão manual solicitada")
            st.rerun()

    with ac8:
        with st.popover("↔️ Reatribuir"):
            analysts = ds.get_analysts()
            new_analyst = st.selectbox("Novo analista", analysts["name"].tolist(), key="reassign_sel")
            if st.button("Confirmar", key="reassign_confirm"):
                cs.reassign(case_id, new_analyst, current_user)
                st.success(f"Caso reatribuído para {new_analyst}")
                st.rerun()

    # Status change inline
    with st.expander("🔄 Alterar Status", expanded=False):
        col_s, col_b = st.columns([3, 1])
        with col_s:
            new_status = st.selectbox("Novo Status", STATUS_OPTIONS, index=STATUS_OPTIONS.index(case.get("status", "Aberto")), key="change_status")
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Aplicar", key="apply_status"):
                cs.change_status(case_id, new_status, current_user)
                st.success(f"Status alterado para {new_status}")
                st.rerun()

    st.divider()

    # ── Main tabs ─────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Visão 360", "🤖 Assistente", "💬 Comentários", "📋 Timeline", "🔗 Relacionamentos"])

    customer = ds.get_customer(str(case.get("customer_id", "")))
    transaction = ds.get_transaction(str(case.get("transaction_id", "")))
    device = ds.get_device(str(case.get("device_id", "")))
    alerts = ds.get_alerts_for_case(case_id)
    comments = ds.get_comments_for_case(case_id)
    history = ds.get_history_for_case(case_id)
    related = ds.get_related_for_case(case_id)

    # ── Tab 1: 360 View ───────────────────────────────────────────────
    with tab1:
        sec1, sec2 = st.columns(2)

        with sec1:
            # 3.1 Case summary
            st.markdown(section_header("📋 Resumo do Caso"), unsafe_allow_html=True)
            summary_fields = [
                ("Case ID", case_id, True),
                ("Tipo de Fraude", case.get("fraud_type", "-")),
                ("Produto", case.get("product", "-")),
                ("Canal", case.get("channel", "-")),
                ("Fila", case.get("queue", "-")),
                ("Analista", case.get("assigned_analyst") or "Não atribuído"),
                ("Origem do Alerta", case.get("alert_source", "-")),
                ("Data de Abertura", format_datetime(pd.to_datetime(case.get("created_at")))),
                ("SLA", f"{'⏰ VENCIDO — ' if sla_overdue else ''}{format_datetime(sla_due)}"),
                ("Valor em Risco", format_currency(case.get("amount_at_risk", 0)), True),
            ]
            html = '<div style="background:#fff;border:1px solid #E0E4EB;border-radius:10px;padding:14px;">'
            for item in summary_fields:
                label, value = item[0], item[1]
                bold = len(item) > 2 and item[2]
                html += info_row(label, str(value), bold)
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

        with sec2:
            # 3.2 Customer
            st.markdown(section_header("👤 Dados do Cliente"), unsafe_allow_html=True)
            if customer:
                fraud_hist = "⚠️ Sim" if customer.get("previous_fraud_flag") else "✅ Não"
                cust_fields = [
                    ("Customer ID", customer.get("customer_id", "-"), True),
                    ("Nome", customer.get("customer_name", "-"), True),
                    ("Documento", customer.get("document_masked", "-")),
                    ("Segmento", customer.get("segment", "-")),
                    ("Cidade/Estado", f"{customer.get('city','-')}, {customer.get('state','-')}"),
                    ("Idade da Conta", f"{customer.get('account_age_days', 0)} dias"),
                    ("Histórico de Fraude", fraud_hist),
                    ("Mudança Cadastral", "⚠️ Sim" if customer.get("profile_change_recent_flag") else "Não"),
                    ("Troca de Telefone", "⚠️ Sim" if customer.get("phone_change_flag") else "Não"),
                    ("Troca de E-mail", "⚠️ Sim" if customer.get("email_change_flag") else "Não"),
                    ("Troca de Endereço", "⚠️ Sim" if customer.get("address_change_flag") else "Não"),
                ]
                html = '<div style="background:#fff;border:1px solid #E0E4EB;border-radius:10px;padding:14px;">'
                for label, value, *rest in cust_fields:
                    html += info_row(label, str(value), bool(rest))
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("Dados do cliente não encontrados.")

        sec3, sec4 = st.columns(2)

        with sec3:
            # 3.3 Transaction
            st.markdown(section_header("💳 Dados da Transação"), unsafe_allow_html=True)
            if transaction:
                inconsistencies = []
                if transaction.get("is_international") and transaction.get("amount", 0) > 5000:
                    inconsistencies.append("Transação internacional de alto valor")
                if transaction.get("velocity_1h", 0) > 8:
                    inconsistencies.append(f"Alta velocity: {transaction.get('velocity_1h')} txns/hora")
                inc_text = "; ".join(inconsistencies) if inconsistencies else "Nenhuma detectada"
                txn_fields = [
                    ("Transaction ID", transaction.get("transaction_id", "-"), True),
                    ("Data/Hora", format_datetime(pd.to_datetime(transaction.get("transaction_timestamp")))),
                    ("Valor", format_currency(transaction.get("amount", 0)), True),
                    ("Canal", transaction.get("channel", "-")),
                    ("Merchant", transaction.get("merchant_name", "-")),
                    ("MCC", transaction.get("mcc", "-")),
                    ("Localização", transaction.get("location", "-")),
                    ("Autenticação", transaction.get("auth_method", "-")),
                    ("IP", transaction.get("ip_address", "-")),
                    ("Velocity 1h", str(transaction.get("velocity_1h", 0))),
                    ("Velocity 24h", str(transaction.get("velocity_24h", 0))),
                    ("Internacional", "⚠️ Sim" if transaction.get("is_international") else "Não"),
                    ("Inconsistências", inc_text),
                ]
                html = '<div style="background:#fff;border:1px solid #E0E4EB;border-radius:10px;padding:14px;">'
                for label, value, *rest in txn_fields:
                    html += info_row(label, str(value), bool(rest))
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("Dados da transação não encontrados.")

        with sec4:
            # 3.4 Device
            st.markdown(section_header("📱 Dados do Dispositivo"), unsafe_allow_html=True)
            if device:
                risk_flags = []
                if device.get("rooted_flag"):    risk_flags.append("Root/Jailbreak")
                if device.get("emulator_flag"):  risk_flags.append("Emulador")
                if device.get("proxy_flag"):     risk_flags.append("Proxy")
                if device.get("vpn_flag"):       risk_flags.append("VPN")
                dev_fields = [
                    ("Device ID", device.get("device_id", "-"), True),
                    ("Fingerprint", device.get("fingerprint", "-")[:16] + "..."),
                    ("Sistema Operacional", device.get("os", "-")),
                    ("Versão do App", device.get("app_version", "-")),
                    ("Root/Jailbreak", "⚠️ Sim" if device.get("rooted_flag") else "Não"),
                    ("Emulador", "⚠️ Sim" if device.get("emulator_flag") else "Não"),
                    ("Proxy", "⚠️ Sim" if device.get("proxy_flag") else "Não"),
                    ("VPN", "⚠️ Sim" if device.get("vpn_flag") else "Não"),
                    ("Contas Vinculadas", str(device.get("linked_accounts_count", 0))),
                    ("Flags de Risco", ", ".join(risk_flags) if risk_flags else "Nenhuma"),
                ]
                html = '<div style="background:#fff;border:1px solid #E0E4EB;border-radius:10px;padding:14px;">'
                for label, value, *rest in dev_fields:
                    html += info_row(label, str(value), bool(rest))
                html += "</div>"
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("Dados do dispositivo não encontrados.")

        # 3.5 Alerts/Risk signals
        st.markdown(section_header("⚠️ Regras e Sinais de Risco"), unsafe_allow_html=True)
        if not alerts.empty:
            cols_show = ["rule_name", "model_score", "reason_code", "risk_signal", "signal_value", "severity", "alert_source", "alert_timestamp"]
            cols_show = [c for c in cols_show if c in alerts.columns]
            st.dataframe(alerts[cols_show].rename(columns={
                "rule_name": "Regra", "model_score": "Score", "reason_code": "Reason Code",
                "risk_signal": "Sinal", "signal_value": "Valor", "severity": "Severidade",
                "alert_source": "Origem", "alert_timestamp": "Timestamp",
            }), use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum alerta vinculado a este caso.")

    # ── Tab 2: AI Assistant ───────────────────────────────────────────
    with tab2:
        render_ai_assistant(case, customer, transaction, device)

    # ── Tab 3: Comments ───────────────────────────────────────────────
    with tab3:
        render_comments_section(case_id, comments, cs, current_user)

    # ── Tab 4: Timeline ───────────────────────────────────────────────
    with tab4:
        render_timeline(history)

    # ── Tab 5: Related entities ───────────────────────────────────────
    with tab5:
        st.markdown("#### 🔗 Entidades Relacionadas")
        if not related.empty:
            cols_show = ["entity_type", "entity_value", "related_case_id", "relation_strength"]
            cols_show = [c for c in cols_show if c in related.columns]
            styled = related[cols_show].rename(columns={
                "entity_type": "Tipo", "entity_value": "Valor (mascarado)",
                "related_case_id": "Caso Relacionado", "relation_strength": "Força",
            })
            st.dataframe(styled, use_container_width=True, hide_index=True)

            # Network visualization (text-based for simplicity)
            st.markdown("**Mapa de Relacionamentos:**")
            entity_types = related["entity_type"].value_counts()
            for etype, count in entity_types.items():
                color_map = {"CPF": "🔴", "Device": "🔵", "Email": "🟡", "Telefone": "🟢",
                             "Endereço": "🟠", "IP": "🟣", "Conta": "⚪"}
                icon = color_map.get(etype, "⚫")
                st.markdown(
                    f'<div style="display:inline-block;background:#F0F4FF;border:1px solid #C5D0E8;'
                    f'border-radius:20px;padding:6px 14px;margin:4px;font-size:13px;">'
                    f'{icon} {etype} ({count})</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("Nenhuma entidade relacionada encontrada para este caso.")
