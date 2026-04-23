# 🛡️ Anti-Fraude Case Manager

Protótipo enterprise de Case Manager para operações de prevenção à fraude, construído com Streamlit e pronto para deploy como Databricks App.

## Arquitetura

```
anti-fraude/
├── main.py                    # Entry point — navegação e roteamento
├── app.yaml                   # Configuração do Databricks App
├── requirements.txt
├── data/
│   └── mock_data.py           # Gerador de dados sintéticos realistas
├── services/
│   ├── data_service.py        # Camada de persistência (Delta + fallback mock)
│   ├── case_service.py        # Operações de negócio nos casos
│   └── heuristics.py          # Motor de regras e recomendações
├── pages/
│   ├── dashboard.py           # Dashboard executivo com KPIs e gráficos
│   ├── case_queue.py          # Fila operacional de casos
│   ├── case_detail.py         # Visão 360 do caso (tabs)
│   └── management.py          # Gestão operacional — produtividade e SLA
├── components/
│   ├── styles.py              # CSS global + helpers de HTML
│   ├── timeline.py            # Timeline de auditoria
│   ├── comments.py            # Seção de comentários do analista
│   └── ai_assistant.py       # Painel de recomendação assistida
├── utils/
│   ├── constants.py           # Enums, cores por status/prioridade
│   └── formatting.py          # Formatação de moeda, data, badges
└── notebooks/
    └── 01_setup_tables.py    # Bootstrap das tabelas Delta no Unity Catalog
```

## Funcionalidades

| Módulo | Funcionalidades |
|--------|----------------|
| Dashboard Executivo | KPIs, gráficos de backlog, distribuição, heatmap, evolução temporal |
| Fila de Casos | Busca, filtros avançados, ordenação, destaque visual por SLA/prioridade |
| Visão 360 do Caso | Caso, cliente, transação, dispositivo, alertas, relacionamentos |
| Ações do Analista | Atribuir, escalar, confirmar fraude, falso positivo, bloquear, solicitar docs |
| Assistente de Investigação | Regras disparadas, fatores de risco, recomendação, próximos passos |
| Comentários | Categorias, destaque importante, histórico cronológico |
| Timeline/Auditoria | Histórico completo de ações com timestamps |
| Gestão Operacional | Produtividade por analista, backlog por fila, aging, SLA, heatmap |

## Execução Local

```bash
cd /caminho/para/anti-fraude
pip install -r requirements.txt
streamlit run main.py
```

## Deploy no Databricks Apps

### 1. Fazer upload dos arquivos para o Workspace

```bash
databricks workspace import_dir ./anti-fraude \
  /Workspace/Users/fernando.custodio@databricks.com/anti-fraude \
  --overwrite
```

### 2. Criar o App

```bash
databricks apps create anti-fraude \
  --description "Case Manager Antifraude"
```

### 3. Deploy

```bash
databricks apps deploy anti-fraude \
  --source-code-path /Workspace/Users/fernando.custodio@databricks.com/anti-fraude
```

### 4. (Opcional) Criar tabelas Delta

Execute o notebook `notebooks/01_setup_tables.py` em qualquer cluster com acesso ao Unity Catalog `fc_vm_catalog`.

## Dados

### Modo Mock (padrão)
A aplicação detecta automaticamente se há Spark disponível. Sem Spark, usa dados gerados em memória — ideal para demo local ou App standalone.

### Modo Delta (produção)
Com Spark ativo (cluster attached ou Databricks Connect), a app lê/escreve em `fc_vm_catalog.anti_fraude.*`. Execute `notebooks/01_setup_tables.py` antes.

### Tabelas criadas
| Tabela | Registros (demo) | Descrição |
|--------|-------------------|-----------|
| fraud_cases | 120 | Casos principais |
| fraud_alerts | ~350 | Alertas vinculados aos casos |
| customers | 80 | Clientes |
| transactions | 150 | Transações |
| devices | 60 | Dispositivos |
| case_comments | ~300 | Comentários dos analistas |
| case_history | ~700 | Histórico de ações |
| related_entities | ~200 | Relacionamentos |
| analysts | 6 | Analistas |
| fraud_rules_catalog | 9 | Catálogo de regras |

## Evolução para Produção

### Integração com dados reais
1. Substitua `data/mock_data.py` por conectores reais
2. Em `services/data_service.py`, ajuste os nomes de tabela conforme seu esquema
3. Adicione autenticação OAuth/LDAP se necessário

### Integração com LLM (Assistente)
Em `services/heuristics.py`, a função `apply_risk_rules()` pode ser substituída por:
```python
from anthropic import Anthropic
client = Anthropic()
# Chamar modelo com contexto do caso e retornar análise estruturada
```

### Adicionar modelos ML reais
O campo `risk_score` pode ser alimentado em tempo real via:
- Feature Store do Databricks
- Model Serving endpoint
- Jobs de scoring batch

## Filtros Globais Disponíveis

- Período, Status, Criticidade, Tipo de Fraude
- Canal, Fila, Analista, Origem do Alerta

## Regras Heurísticas Implementadas

- Score > 900 → Prioridade Crítica, recomendar Bloquear
- Score 800–900 → Alta, recomendar Confirmar Fraude
- Score 650–800 → Média, recomendar Revisar Manualmente
- Score < 650 → Baixa, recomendar Aprovar
- Transação internacional + valor > R$ 5.000 → risco agravado
- Velocity > 8 txns/hora → agravante
- Mudança cadastral recente → agravante
- Device com root/emulador → risco crítico
- VPN/Proxy detectado → agravante
- Múltiplas contas no device → agravante
- Histórico de fraude → agravante
- Conta > 365 dias, autenticação forte → mitigantes
