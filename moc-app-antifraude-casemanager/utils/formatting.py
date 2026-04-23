from utils.constants import STATUS_COLORS, PRIORITY_COLORS, ACTION_COLORS
from datetime import datetime


def format_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage(value: float) -> str:
    return f"{value * 100:.1f}%"


def format_datetime(dt) -> str:
    if dt is None:
        return "-"
    try:
        if hasattr(dt, "strftime"):
            return dt.strftime("%d/%m/%Y %H:%M")
        return str(dt)
    except Exception:
        return str(dt)


def format_aging(created_at) -> str:
    try:
        now = datetime.now()
        delta = now - created_at
        hours = delta.total_seconds() / 3600
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)}min"
        elif hours < 24:
            return f"{int(hours)}h"
        else:
            return f"{int(hours / 24)}d {int(hours % 24)}h"
    except Exception:
        return "-"


def get_status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, "#666")
    return f'<span style="background:{color}22;color:{color};border:1px solid {color};border-radius:12px;padding:2px 10px;font-size:12px;font-weight:600;">{status}</span>'


def get_priority_badge(priority: str) -> str:
    color = PRIORITY_COLORS.get(priority, "#666")
    emoji = {"Crítica": "🔴", "Alta": "🟠", "Média": "🟡", "Baixa": "🟢"}.get(priority, "⚪")
    return f'<span style="background:{color}22;color:{color};border:1px solid {color};border-radius:12px;padding:2px 10px;font-size:12px;font-weight:600;">{emoji} {priority}</span>'


def get_action_badge(action: str) -> str:
    color = ACTION_COLORS.get(action, "#666")
    return f'<span style="background:{color}22;color:{color};border:1px solid {color};border-radius:12px;padding:2px 10px;font-size:12px;font-weight:600;">{action}</span>'


def get_score_color(score: int) -> str:
    if score >= 900:
        return "#D32F2F"
    elif score >= 750:
        return "#F57C00"
    elif score >= 600:
        return "#FBC02D"
    return "#388E3C"


def is_sla_overdue(sla_due_at) -> bool:
    try:
        return datetime.now() > sla_due_at
    except Exception:
        return False
