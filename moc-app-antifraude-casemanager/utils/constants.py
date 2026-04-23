STATUS_OPTIONS = ["Aberto", "Em Investigação", "Aguardando Documentação", "Encerrado", "Escalado"]
PRIORITY_OPTIONS = ["Crítica", "Alta", "Média", "Baixa"]
SEVERITY_OPTIONS = ["Crítica", "Alta", "Média", "Baixa"]
FRAUD_TYPES = [
    "Fraude de Identidade", "Fraude de Cartão", "Account Takeover",
    "Phishing", "Engenharia Social", "Fraude PIX", "Lavagem de Dinheiro", "Fraude de Crédito"
]
CHANNELS = ["App Mobile", "Web", "ATM", "POS", "Call Center", "API"]
QUEUES = ["Fraude Digital", "Fraude Identidade", "Revisão Manual", "Alta Complexidade"]
PRODUCTS = ["Cartão de Crédito", "Cartão de Débito", "PIX", "TED", "Conta Digital", "Empréstimo", "Seguro"]
ALERT_SOURCES = ["Motor de Regras", "Modelo ML", "Denúncia Cliente", "Compliance", "Parceiro"]
RECOMMENDED_ACTIONS = ["Aprovar", "Revisar Manualmente", "Bloquear Preventivamente", "Confirmar Fraude"]
COMMENT_TYPES = ["investigação", "contato cliente", "evidência", "decisão", "observação"]

STATUS_COLORS = {
    "Aberto": "#1976D2",
    "Em Investigação": "#F57C00",
    "Aguardando Documentação": "#7B1FA2",
    "Encerrado": "#388E3C",
    "Escalado": "#D32F2F",
}
PRIORITY_COLORS = {
    "Crítica": "#D32F2F",
    "Alta": "#F57C00",
    "Média": "#FBC02D",
    "Baixa": "#388E3C",
}
ACTION_COLORS = {
    "Aprovar": "#388E3C",
    "Revisar Manualmente": "#F57C00",
    "Bloquear Preventivamente": "#D32F2F",
    "Confirmar Fraude": "#B71C1C",
}

UNITY_CATALOG = "fc_vm_catalog"
SCHEMA = "anti_fraude"
