"""
Heuristics engine — deterministic risk enrichment.
Architecture is ready to be replaced by real ML model calls.
"""
from datetime import datetime


def apply_risk_rules(case: dict, customer: dict, transaction: dict, device: dict) -> dict:
    """Return a dict with triggered rules, aggravating factors, and risk explanation."""
    rules_triggered = []
    aggravating = []
    mitigating = []
    score = case.get("risk_score", 500)

    # --- Score-based priority ---
    if score > 900:
        rules_triggered.append({"rule": "SCORE_CRITICO", "description": "Score de risco acima de 900", "severity": "Crítica"})
    elif score > 750:
        rules_triggered.append({"rule": "SCORE_ALTO", "description": "Score de risco entre 750 e 900", "severity": "Alta"})

    # --- International transaction + high value ---
    txn_amount = transaction.get("amount", 0) if transaction else 0
    is_intl = transaction.get("is_international", False) if transaction else False
    if is_intl and txn_amount > 5000:
        rules_triggered.append({"rule": "REGRA_INTL_VALOR_ALTO", "description": f"Transação internacional de R$ {txn_amount:,.2f}", "severity": "Alta"})
        aggravating.append("Transação internacional com valor elevado")

    # --- High velocity ---
    v1h = transaction.get("velocity_1h", 0) if transaction else 0
    v24h = transaction.get("velocity_24h", 0) if transaction else 0
    if v1h > 8:
        rules_triggered.append({"rule": "REGRA_VELOCITY_ALTA", "description": f"{v1h} transações na última hora", "severity": "Alta"})
        aggravating.append(f"Alta velocidade de transações: {v1h} em 1h / {v24h} em 24h")

    # --- Recent profile changes ---
    profile_change = customer.get("profile_change_recent_flag", False) if customer else False
    phone_change = customer.get("phone_change_flag", False) if customer else False
    email_change = customer.get("email_change_flag", False) if customer else False
    address_change = customer.get("address_change_flag", False) if customer else False

    if profile_change:
        changes = []
        if phone_change:
            changes.append("telefone")
        if email_change:
            changes.append("e-mail")
        if address_change:
            changes.append("endereço")
        label = ", ".join(changes) if changes else "dados cadastrais"
        rules_triggered.append({"rule": "REGRA_CADASTRO_RECENTE", "description": f"Mudança recente de {label}", "severity": "Média"})
        aggravating.append(f"Alteração cadastral recente: {label}")
        if v1h > 3:
            aggravating.append("Mudança cadastral recente combinada com alta velocidade")

    # --- Device risk ---
    if device:
        linked = device.get("linked_accounts_count", 1)
        if linked > 3:
            rules_triggered.append({"rule": "REGRA_MULTI_CONTA_DEVICE", "description": f"Device com {linked} contas vinculadas", "severity": "Alta"})
            aggravating.append(f"Device compartilhado: {linked} contas associadas")
        if device.get("rooted_flag") or device.get("emulator_flag"):
            rules_triggered.append({"rule": "REGRA_DEVICE_COMPROMETIDO", "description": "Device com root/jailbreak ou emulador detectado", "severity": "Crítica"})
            aggravating.append("Device comprometido (root/emulador)")
        if device.get("vpn_flag") or device.get("proxy_flag"):
            rules_triggered.append({"rule": "REGRA_VPN_PROXY", "description": "Uso de VPN ou proxy detectado", "severity": "Média"})
            aggravating.append("Conexão via VPN/proxy")

    # --- Previous fraud history ---
    prev_fraud = customer.get("previous_fraud_flag", False) if customer else False
    if prev_fraud:
        rules_triggered.append({"rule": "HISTORICO_FRAUDE", "description": "Cliente com histórico prévio de fraude", "severity": "Alta"})
        aggravating.append("Histórico de fraude confirmada anteriormente")

    # --- Mitigating factors ---
    account_age = customer.get("account_age_days", 0) if customer else 0
    if account_age > 365:
        mitigating.append(f"Conta com {account_age} dias de histórico positivo")
    if not profile_change:
        mitigating.append("Sem alterações cadastrais recentes")
    if v1h <= 2:
        mitigating.append("Baixa frequência de transações recentes")
    if not is_intl:
        mitigating.append("Transação doméstica")
    auth = transaction.get("auth_method", "") if transaction else ""
    if auth in ("Biometria", "Token App"):
        mitigating.append(f"Autenticação forte utilizada: {auth}")

    # --- Recommendation ---
    recommended = case.get("recommended_action", "Revisar Manualmente")
    confidence = _confidence(score, len(aggravating), len(mitigating))

    # --- Next steps ---
    next_steps = _build_next_steps(recommended, aggravating, customer, device)

    return {
        "rules_triggered": rules_triggered,
        "aggravating": aggravating,
        "mitigating": mitigating,
        "recommended_action": recommended,
        "confidence": confidence,
        "next_steps": next_steps,
        "summary": _build_summary(case, customer, transaction, device, aggravating, mitigating),
    }


def _confidence(score: int, n_aggr: int, n_mit: int) -> str:
    net = n_aggr - n_mit
    if score > 900 and net >= 2:
        return "Alta (>90%)"
    elif score > 750 and net >= 1:
        return "Alta (>80%)"
    elif score > 600:
        return "Média (60–80%)"
    return "Baixa (<60%)"


def _build_next_steps(action: str, aggravating: list, customer: dict, device: dict) -> list:
    steps = []
    if action == "Bloquear Preventivamente":
        steps.append("Acionar bloqueio preventivo da conta/cartão imediatamente")
        steps.append("Notificar cliente por SMS e e-mail sobre bloqueio")
        steps.append("Registrar decisão e evidências no histórico do caso")
    elif action == "Confirmar Fraude":
        steps.append("Confirmar fraude e acionar processo de ressarcimento")
        steps.append("Encaminhar para equipe de recuperação de ativos")
        steps.append("Reportar ao Bacen se aplicável (RIF)")
    elif action == "Revisar Manualmente":
        steps.append("Tentar contato com o cliente para validar transação")
        steps.append("Analisar histórico completo de transações dos últimos 30 dias")
        steps.append("Verificar se há casos relacionados no mesmo device/CPF")
    else:
        steps.append("Validar transação e liberar se sem outros indícios")
        steps.append("Monitorar conta por 48h antes de encerrar caso")

    if customer and customer.get("profile_change_recent_flag"):
        steps.append("Confirmar identidade do cliente via canal seguro antes de qualquer liberação")
    if device and device.get("linked_accounts_count", 1) > 3:
        steps.append("Investigar outras contas vinculadas ao mesmo dispositivo")

    return steps


def _build_summary(case, customer, transaction, device, aggravating, mitigating) -> str:
    name = customer.get("customer_name", "Cliente") if customer else "Cliente"
    score = case.get("risk_score", 0)
    amount = transaction.get("amount", 0) if transaction else case.get("amount_at_risk", 0)
    fraud_type = case.get("fraud_type", "suspeita")

    summary = (
        f"Caso de {fraud_type} referente ao cliente **{name}** com score de risco **{score}** "
        f"e valor em risco de **R$ {amount:,.2f}**. "
    )
    if aggravating:
        summary += f"Principais fatores de risco: {'; '.join(aggravating[:3])}. "
    if mitigating:
        summary += f"Fatores que indicam possível legitimidade: {'; '.join(mitigating[:2])}."
    return summary
