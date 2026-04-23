import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string

random.seed(42)
np.random.seed(42)

_FIRST_NAMES = ["Ana", "Carlos", "Mariana", "Rafael", "Juliana", "Pedro", "Fernanda", "Lucas",
                "Camila", "Bruno", "Amanda", "Gustavo", "Patrícia", "Rodrigo", "Vanessa",
                "Thiago", "Renata", "Felipe", "Aline", "Diego", "Cristiane", "Marcelo",
                "Sandra", "Eduardo", "Tatiana", "Roberto", "Priscila", "Leonardo", "Daniela", "André"]
_LAST_NAMES = ["Silva", "Santos", "Oliveira", "Souza", "Costa", "Ferreira", "Lima", "Alves",
               "Mendes", "Ribeiro", "Carvalho", "Araújo", "Nascimento", "Rodrigues", "Gomes",
               "Martins", "Barros", "Pereira", "Melo", "Rocha", "Azevedo", "Cardoso", "Castro",
               "Campos", "Moreira", "Nunes", "Freitas", "Cavalcanti", "Monteiro", "Figueiredo"]
_CITIES = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre",
           "Salvador", "Recife", "Fortaleza", "Manaus", "Brasília"]
_STATES = ["SP", "RJ", "MG", "PR", "RS", "BA", "PE", "CE", "AM", "DF"]
_OS = ["Android 12", "Android 13", "Android 14", "iOS 16", "iOS 17", "Web/Chrome", "Web/Firefox"]
_MERCHANTS = ["iFood", "Mercado Livre", "Amazon BR", "Magazine Luiza", "Shopee", "AliExpress",
              "Americanas", "Uber", "99", "Carrefour", "Posto Shell", "Farmácia São Paulo",
              "Extra", "Pão de Açúcar", "Lojas Americanas", "Submarino"]
_AUTH = ["Biometria", "Senha", "Token SMS", "Token App", "Sem autenticação", "3DS"]
_CHANNELS = ["App Mobile", "Web", "ATM", "POS", "Call Center", "API"]
_FRAUD_TYPES = ["Fraude de Identidade", "Fraude de Cartão", "Account Takeover",
                "Phishing", "Engenharia Social", "Fraude PIX", "Lavagem de Dinheiro", "Fraude de Crédito"]
_QUEUES = ["Fraude Digital", "Fraude Identidade", "Revisão Manual", "Alta Complexidade"]
_PRODUCTS = ["Cartão de Crédito", "Cartão de Débito", "PIX", "TED", "Conta Digital", "Empréstimo", "Seguro"]
_SOURCES = ["Motor de Regras", "Modelo ML", "Denúncia Cliente", "Compliance", "Parceiro"]
_SEGMENTS = ["PF", "PJ", "Premium", "Black", "Varejo"]
_RULES = ["REGRA_VELOCITY_ALTA", "REGRA_INTL_VALOR_ALTO", "REGRA_DEVICE_NOVO",
          "REGRA_CADASTRO_RECENTE", "REGRA_MULTI_CONTA_DEVICE", "REGRA_HORARIO_INCOMUM",
          "MODELO_FRAUDE_V3", "MODELO_ATO_V2", "REGRA_CPF_BLOQUEADO"]
_REASON_CODES = ["HIGH_VELOCITY", "INTL_HIGH_AMOUNT", "NEW_DEVICE", "RECENT_PROFILE_CHANGE",
                 "MULTI_ACCOUNT_DEVICE", "UNUSUAL_HOUR", "MODEL_HIGH_SCORE", "KNOWN_FRAUD_ENTITY", "BLOCKED_DOCUMENT"]
_RISK_SIGNALS = ["velocity_anomaly", "international_transaction", "device_anomaly", "profile_change",
                 "linked_accounts", "time_anomaly", "model_score", "blacklist_hit", "geolocation_mismatch"]
_COMMENT_TEMPLATES = {
    "investigação": [
        "Análise de transações dos últimos 30 dias não indica padrão suspeito anterior.",
        "Verificado histórico do cliente, encontrado comportamento atípico nas últimas 48h.",
        "IP utilizado na transação consta em lista negra de provedores de proxy.",
        "Device nunca utilizado anteriormente pelo cliente — first seen today.",
        "Consulta em bureau de crédito retornou 3 ocorrências de fraude no CPF.",
    ],
    "contato cliente": [
        "Tentativa de contato por telefone sem sucesso — 3 tentativas realizadas.",
        "Cliente confirmou não ter realizado a transação suspeita.",
        "Cliente informou que está viajando internacionalmente e realizou a transação.",
        "Aguardando retorno do cliente via canal digital (app e e-mail enviados).",
        "Cliente acionou central de atendimento relatando perda do celular.",
    ],
    "evidência": [
        "Screenshot de conversa suspeita via WhatsApp adicionado ao caso.",
        "Comprovante de transação enviado pelo cliente para análise.",
        "Logs de geolocalização inconsistentes: transação em SP e acesso simultâneo em MG.",
        "Logs de acesso indicam uso de emulador Android — flags detectados.",
        "Captura de tela da tentativa de phishing enviada pelo cliente.",
    ],
    "decisão": [
        "Caso encaminhado para bloqueio preventivo da conta — aguardando confirmação.",
        "Após análise detalhada, classificado como falso positivo. Transação aprovada.",
        "Fraude confirmada — acionado processo de ressarcimento ao cliente.",
        "Escalado para equipe de Alta Complexidade por envolver múltiplas vítimas.",
        "Decisão: revisar após contato com cliente nas próximas 24h.",
    ],
    "observação": [
        "Caso relacionado a outros 3 casos ativos no mesmo device_id.",
        "Padrão similar ao observado na operação de fraude detectada no mês passado.",
        "Aguardando análise complementar do parceiro merchant.",
        "Risco agravado por mudança de endereço realizada há 5 dias.",
        "Cliente possui histórico de acionamento de seguros — investigar correlação.",
    ],
}


def _rand_name():
    return f"{random.choice(_FIRST_NAMES)} {random.choice(_LAST_NAMES)}"


def _rand_hex(n=32):
    return "".join(random.choices(string.hexdigits, k=n)).lower()


def generate_analysts():
    return pd.DataFrame([
        {"analyst_id": "ANA001", "name": "Ana Souza", "email": "ana.souza@empresa.com",
         "team": "Fraude Digital", "queue": "Cartão", "level": "Senior"},
        {"analyst_id": "ANA002", "name": "Carlos Lima", "email": "carlos.lima@empresa.com",
         "team": "Fraude Digital", "queue": "PIX", "level": "Pleno"},
        {"analyst_id": "ANA003", "name": "Mariana Costa", "email": "mariana.costa@empresa.com",
         "team": "Fraude Identidade", "queue": "Conta", "level": "Senior"},
        {"analyst_id": "ANA004", "name": "Rafael Mendes", "email": "rafael.mendes@empresa.com",
         "team": "Fraude Digital", "queue": "Cartão", "level": "Junior"},
        {"analyst_id": "ANA005", "name": "Juliana Ferreira", "email": "juliana.ferreira@empresa.com",
         "team": "Fraude Identidade", "queue": "PIX", "level": "Pleno"},
        {"analyst_id": "ANA006", "name": "Pedro Alves", "email": "pedro.alves@empresa.com",
         "team": "Fraude Digital", "queue": "TED", "level": "Senior"},
    ])


def generate_customers(n=80):
    rows = []
    for i in range(1, n + 1):
        s = random.randint(0, len(_CITIES) - 1)
        rows.append({
            "customer_id": f"CUST{i:06d}",
            "customer_name": _rand_name(),
            "document_masked": f"***.***.***-{random.randint(10,99)}",
            "account_age_days": random.randint(30, 2000),
            "segment": random.choice(_SEGMENTS),
            "city": _CITIES[s],
            "state": _STATES[s],
            "previous_fraud_flag": random.random() < 0.15,
            "profile_change_recent_flag": random.random() < 0.25,
            "phone_change_flag": random.random() < 0.15,
            "email_change_flag": random.random() < 0.1,
            "address_change_flag": random.random() < 0.1,
        })
    return pd.DataFrame(rows)


def generate_devices(n=60):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "device_id": f"DEV{i:06d}",
            "fingerprint": _rand_hex(32),
            "os": random.choice(_OS),
            "app_version": f"{random.randint(3,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
            "rooted_flag": random.random() < 0.08,
            "emulator_flag": random.random() < 0.05,
            "proxy_flag": random.random() < 0.12,
            "vpn_flag": random.random() < 0.18,
            "linked_accounts_count": random.randint(1, 8),
        })
    return pd.DataFrame(rows)


def generate_transactions(customer_ids, device_ids, n=150):
    now = datetime.now()
    rows = []
    for i in range(1, n + 1):
        s = random.randint(0, len(_CITIES) - 1)
        v1 = random.randint(1, 15)
        rows.append({
            "transaction_id": f"TXN{i:08d}",
            "customer_id": random.choice(customer_ids),
            "transaction_timestamp": now - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59)),
            "amount": round(random.uniform(50, 25000), 2),
            "merchant_name": random.choice(_MERCHANTS),
            "mcc": random.choice(["5411", "5812", "5999", "4121", "5912", "7011", "4814", "5311"]),
            "channel": random.choice(_CHANNELS),
            "location": f"{_CITIES[s]}, {_STATES[s]}",
            "auth_method": random.choice(_AUTH),
            "ip_address": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
            "device_id": random.choice(device_ids),
            "is_international": random.random() < 0.15,
            "velocity_1h": v1,
            "velocity_24h": random.randint(v1, 50),
        })
    return pd.DataFrame(rows)


def _score_to_fields(score):
    if score > 900:
        return "Crítica", "Crítica", 4, "Bloquear Preventivamente"
    elif score > 800:
        return "Alta", "Alta", 8, "Confirmar Fraude"
    elif score > 650:
        return "Média", "Média", 24, "Revisar Manualmente"
    return "Baixa", "Baixa", 48, "Aprovar"


def generate_fraud_cases(customer_ids, transaction_ids, device_ids, analyst_names, n=120):
    now = datetime.now()
    statuses = ["Aberto", "Em Investigação", "Aguardando Documentação", "Encerrado", "Escalado"]
    weights = [0.25, 0.30, 0.15, 0.20, 0.10]
    rows = []
    for i in range(1, n + 1):
        score = random.randint(300, 999)
        priority, severity, sla_h, action = _score_to_fields(score)
        created_at = now - timedelta(days=random.randint(0, 45), hours=random.randint(0, 23))
        sla_due = created_at + timedelta(hours=sla_h)
        status = random.choices(statuses, weights=weights, k=1)[0]
        closed_at = None
        if status == "Encerrado":
            closed_at = created_at + timedelta(hours=random.randint(1, sla_h * 2))
        analyst = random.choices(analyst_names + [None], weights=[1] * len(analyst_names) + [0.3], k=1)[0]
        rows.append({
            "case_id": f"CASE{i:06d}",
            "created_at": created_at,
            "updated_at": created_at + timedelta(hours=random.randint(0, 10)),
            "status": status,
            "priority": priority,
            "severity": severity,
            "risk_score": score,
            "recommended_action": action,
            "assigned_analyst": analyst,
            "queue": random.choice(_QUEUES),
            "fraud_type": random.choice(_FRAUD_TYPES),
            "channel": random.choice(_CHANNELS),
            "product": random.choice(_PRODUCTS),
            "amount_at_risk": round(random.uniform(200, 50000), 2),
            "customer_id": random.choice(customer_ids),
            "transaction_id": random.choice(transaction_ids),
            "device_id": random.choice(device_ids),
            "sla_due_at": sla_due,
            "closed_at": closed_at,
            "alert_source": random.choice(_SOURCES),
        })
    return pd.DataFrame(rows)


def generate_fraud_alerts(cases_df):
    rows = []
    alert_id = 1
    for _, case in cases_df.iterrows():
        for _ in range(random.randint(1, 5)):
            idx = random.randint(0, len(_RULES) - 1)
            rows.append({
                "alert_id": f"ALT{alert_id:08d}",
                "case_id": case["case_id"],
                "alert_timestamp": case["created_at"] - timedelta(minutes=random.randint(1, 60)),
                "alert_source": case["alert_source"],
                "rule_name": _RULES[idx],
                "model_score": max(0, min(999, case["risk_score"] + random.randint(-50, 50))),
                "reason_code": _REASON_CODES[idx % len(_REASON_CODES)],
                "risk_signal": _RISK_SIGNALS[idx % len(_RISK_SIGNALS)],
                "signal_value": round(random.uniform(0.1, 10.0), 2),
                "severity": case["severity"],
            })
            alert_id += 1
    return pd.DataFrame(rows)


def generate_case_comments(cases_df, analyst_names):
    rows = []
    cid = 1
    types = list(_COMMENT_TEMPLATES.keys())
    for _, case in cases_df.iterrows():
        for _ in range(random.randint(0, 6)):
            ctype = random.choice(types)
            rows.append({
                "comment_id": f"CMT{cid:08d}",
                "case_id": case["case_id"],
                "author": random.choice(analyst_names),
                "comment_type": ctype,
                "comment_text": random.choice(_COMMENT_TEMPLATES[ctype]),
                "created_at": case["created_at"] + timedelta(hours=random.randint(0, 8), minutes=random.randint(0, 59)),
                "important_flag": random.random() < 0.2,
            })
            cid += 1
    return pd.DataFrame(rows)


def generate_case_history(cases_df, analyst_names):
    action_types = ["Mudança de Status", "Atribuição", "Comentário", "Bloqueio", "Escalamento", "Decisão", "Solicitação Documentação"]
    rows = []
    hid = 1
    for _, case in cases_df.iterrows():
        rows.append({
            "history_id": f"HIS{hid:08d}",
            "case_id": case["case_id"],
            "action_type": "Criação",
            "old_value": None,
            "new_value": "Aberto",
            "action_by": "Sistema",
            "action_timestamp": case["created_at"],
        })
        hid += 1
        ts = case["created_at"]
        for _ in range(random.randint(1, 5)):
            ts = ts + timedelta(hours=random.randint(0, 3))
            action = random.choice(action_types)
            rows.append({
                "history_id": f"HIS{hid:08d}",
                "case_id": case["case_id"],
                "action_type": action,
                "old_value": random.choice(["Aberto", "Em Investigação", None]),
                "new_value": random.choice(["Em Investigação", "Encerrado", "Escalado", case["assigned_analyst"]]),
                "action_by": random.choice(analyst_names),
                "action_timestamp": ts,
            })
            hid += 1
    return pd.DataFrame(rows)


def generate_related_entities(cases_df):
    entity_types = ["CPF", "Device", "Email", "Telefone", "Endereço", "IP", "Conta"]
    case_ids = cases_df["case_id"].tolist()
    rows = []
    rid = 1
    sample = cases_df.to_dict("records")  # todos os cases têm relacionamentos
    for case in sample:
        for _ in range(random.randint(1, 4)):
            rows.append({
                "relation_id": f"REL{rid:08d}",
                "case_id": case["case_id"],
                "entity_type": random.choice(entity_types),
                "entity_value": f"***masked{random.randint(100,999)}***",
                "related_case_id": random.choice(case_ids),
                "relation_strength": round(random.uniform(0.3, 1.0), 2),
                "created_at": case["created_at"],
            })
            rid += 1
    return pd.DataFrame(rows)


def generate_fraud_rules_catalog():
    return pd.DataFrame([
        {"rule_id": "R001", "rule_name": "REGRA_VELOCITY_ALTA", "description": "Mais de 10 transações em 1 hora", "category": "Velocity", "weight": 0.80, "active": True},
        {"rule_id": "R002", "rule_name": "REGRA_INTL_VALOR_ALTO", "description": "Transação internacional acima de R$ 5.000", "category": "Valor", "weight": 0.90, "active": True},
        {"rule_id": "R003", "rule_name": "REGRA_DEVICE_NOVO", "description": "Dispositivo não reconhecido pelo cliente", "category": "Device", "weight": 0.70, "active": True},
        {"rule_id": "R004", "rule_name": "REGRA_CADASTRO_RECENTE", "description": "Mudança cadastral nos últimos 7 dias", "category": "Identidade", "weight": 0.75, "active": True},
        {"rule_id": "R005", "rule_name": "REGRA_MULTI_CONTA_DEVICE", "description": "Device com mais de 3 contas associadas", "category": "Device", "weight": 0.85, "active": True},
        {"rule_id": "R006", "rule_name": "REGRA_HORARIO_INCOMUM", "description": "Transação em horário incomum (02h–05h)", "category": "Comportamento", "weight": 0.50, "active": True},
        {"rule_id": "R007", "rule_name": "REGRA_CPF_BLOQUEADO", "description": "CPF consta em lista de entidades suspeitas", "category": "Blacklist", "weight": 1.00, "active": True},
        {"rule_id": "R008", "rule_name": "MODELO_FRAUDE_V3", "description": "Score do modelo de fraude de cartão >= 0.80", "category": "Modelo ML", "weight": 0.95, "active": True},
        {"rule_id": "R009", "rule_name": "MODELO_ATO_V2", "description": "Score do modelo de Account Takeover >= 0.75", "category": "Modelo ML", "weight": 0.90, "active": True},
    ])


def generate_all():
    analysts = generate_analysts()
    analyst_names = analysts["name"].tolist()

    customers = generate_customers(80)
    devices = generate_devices(60)
    customer_ids = customers["customer_id"].tolist()
    device_ids = devices["device_id"].tolist()

    transactions = generate_transactions(customer_ids, device_ids, 150)
    transaction_ids = transactions["transaction_id"].tolist()

    cases = generate_fraud_cases(customer_ids, transaction_ids, device_ids, analyst_names, 120)
    alerts = generate_fraud_alerts(cases)
    comments = generate_case_comments(cases, analyst_names)
    history = generate_case_history(cases, analyst_names)
    related = generate_related_entities(cases)
    rules = generate_fraud_rules_catalog()

    return {
        "fraud_cases": cases,
        "fraud_alerts": alerts,
        "customers": customers,
        "transactions": transactions,
        "devices": devices,
        "case_comments": comments,
        "case_history": history,
        "related_entities": related,
        "analysts": analysts,
        "fraud_rules_catalog": rules,
    }
