"""
Case service — business operations on top of DataService.
"""
from datetime import datetime
from services.data_service import DataService
from utils.constants import STATUS_OPTIONS


class CaseService:
    def __init__(self, ds: DataService):
        self.ds = ds

    def assign_to_me(self, case_id: str, analyst: str):
        case = self.ds.get_case(case_id)
        old = case.get("assigned_analyst")
        self.ds.update_case(case_id, {"assigned_analyst": analyst, "status": "Em Investigação"})
        self.ds.add_history(case_id, "Atribuição", old, analyst, analyst)
        self.ds.add_history(case_id, "Mudança de Status", case.get("status"), "Em Investigação", analyst)

    def reassign(self, case_id: str, new_analyst: str, by: str):
        case = self.ds.get_case(case_id)
        old = case.get("assigned_analyst")
        self.ds.update_case(case_id, {"assigned_analyst": new_analyst})
        self.ds.add_history(case_id, "Atribuição", old, new_analyst, by)

    def change_status(self, case_id: str, new_status: str, by: str):
        case = self.ds.get_case(case_id)
        old_status = case.get("status")
        updates = {"status": new_status}
        if new_status == "Encerrado":
            updates["closed_at"] = datetime.now()
        self.ds.update_case(case_id, updates)
        self.ds.add_history(case_id, "Mudança de Status", old_status, new_status, by)

    def add_comment(self, case_id: str, author: str, ctype: str, text: str, important: bool):
        self.ds.add_comment(case_id, author, ctype, text, important)
        self.ds.add_history(case_id, "Comentário", None, f"[{ctype}] adicionado", author)

    def confirm_fraud(self, case_id: str, by: str):
        self.ds.update_case(case_id, {
            "status": "Encerrado",
            "recommended_action": "Confirmar Fraude",
            "closed_at": datetime.now(),
        })
        self.ds.add_history(case_id, "Decisão", None, "Fraude Confirmada", by)

    def mark_false_positive(self, case_id: str, by: str):
        self.ds.update_case(case_id, {
            "status": "Encerrado",
            "recommended_action": "Aprovar",
            "closed_at": datetime.now(),
        })
        self.ds.add_history(case_id, "Decisão", None, "Falso Positivo", by)

    def escalate(self, case_id: str, by: str):
        case = self.ds.get_case(case_id)
        self.ds.update_case(case_id, {
            "status": "Escalado",
            "queue": "Alta Complexidade",
            "priority": "Crítica",
        })
        self.ds.add_history(case_id, "Escalamento", case.get("status"), "Escalado — Alta Complexidade", by)

    def block_preventive(self, case_id: str, by: str):
        self.ds.update_case(case_id, {
            "recommended_action": "Bloquear Preventivamente",
            "status": "Em Investigação",
        })
        self.ds.add_history(case_id, "Bloqueio", None, "Bloqueio preventivo aplicado", by)

    def request_docs(self, case_id: str, by: str):
        self.ds.update_case(case_id, {"status": "Aguardando Documentação"})
        self.ds.add_history(case_id, "Solicitação Documentação", None, "Documentação solicitada ao cliente", by)

    def request_review(self, case_id: str, by: str):
        self.ds.update_case(case_id, {"status": "Em Investigação", "recommended_action": "Revisar Manualmente"})
        self.ds.add_history(case_id, "Revisão", None, "Revisão manual solicitada", by)
