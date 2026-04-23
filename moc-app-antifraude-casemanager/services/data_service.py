"""
Data service — persistence layer with Delta Tables (Unity Catalog) + in-memory fallback.
All UI code interacts ONLY with this class, never with storage directly.
"""
import pandas as pd
import streamlit as st
from datetime import datetime

try:
    from data.mock_data import generate_all
except ImportError:
    from mock_data import generate_all

CATALOG = "fc_vm_catalog"
SCHEMA = "anti_fraude"


class DataService:
    def __init__(self):
        self._use_delta = self._try_init_spark()
        if not self._use_delta:
            self._load_mock_data()

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _try_init_spark(self) -> bool:
        try:
            from pyspark.sql import SparkSession
            spark = SparkSession.getActiveSession()
            if spark is None:
                return False
            spark.sql(f"USE CATALOG {CATALOG}")
            spark.sql(f"USE SCHEMA {SCHEMA}")
            self._spark = spark
            return True
        except Exception:
            return False

    def _load_mock_data(self):
        self._data = generate_all()

    # ------------------------------------------------------------------
    # Public readers
    # ------------------------------------------------------------------

    def get_fraud_cases(self) -> pd.DataFrame:
        return self._read("fraud_cases")

    def get_fraud_alerts(self) -> pd.DataFrame:
        return self._read("fraud_alerts")

    def get_customers(self) -> pd.DataFrame:
        return self._read("customers")

    def get_transactions(self) -> pd.DataFrame:
        return self._read("transactions")

    def get_devices(self) -> pd.DataFrame:
        return self._read("devices")

    def get_case_comments(self) -> pd.DataFrame:
        return self._read("case_comments")

    def get_case_history(self) -> pd.DataFrame:
        return self._read("case_history")

    def get_related_entities(self) -> pd.DataFrame:
        return self._read("related_entities")

    def get_analysts(self) -> pd.DataFrame:
        return self._read("analysts")

    def get_fraud_rules_catalog(self) -> pd.DataFrame:
        return self._read("fraud_rules_catalog")

    # ------------------------------------------------------------------
    # Convenience single-row lookups
    # ------------------------------------------------------------------

    def get_case(self, case_id: str) -> dict:
        df = self.get_fraud_cases()
        rows = df[df["case_id"] == case_id]
        return rows.iloc[0].to_dict() if len(rows) > 0 else {}

    def get_customer(self, customer_id: str) -> dict:
        df = self.get_customers()
        rows = df[df["customer_id"] == customer_id]
        return rows.iloc[0].to_dict() if len(rows) > 0 else {}

    def get_transaction(self, transaction_id: str) -> dict:
        df = self.get_transactions()
        rows = df[df["transaction_id"] == transaction_id]
        return rows.iloc[0].to_dict() if len(rows) > 0 else {}

    def get_device(self, device_id: str) -> dict:
        df = self.get_devices()
        rows = df[df["device_id"] == device_id]
        return rows.iloc[0].to_dict() if len(rows) > 0 else {}

    def get_alerts_for_case(self, case_id: str) -> pd.DataFrame:
        df = self.get_fraud_alerts()
        return df[df["case_id"] == case_id].sort_values("alert_timestamp", ascending=False)

    def get_comments_for_case(self, case_id: str) -> pd.DataFrame:
        df = self.get_case_comments()
        return df[df["case_id"] == case_id].sort_values("created_at", ascending=False)

    def get_history_for_case(self, case_id: str) -> pd.DataFrame:
        df = self.get_case_history()
        return df[df["case_id"] == case_id].sort_values("action_timestamp", ascending=True)

    def get_related_for_case(self, case_id: str) -> pd.DataFrame:
        df = self.get_related_entities()
        return df[df["case_id"] == case_id]

    # ------------------------------------------------------------------
    # Writers (session-state backed for demo; Delta in production)
    # ------------------------------------------------------------------

    def update_case(self, case_id: str, updates: dict):
        """Update case fields and log history."""
        updates["updated_at"] = datetime.now()
        if self._use_delta:
            self._delta_update("fraud_cases", "case_id", case_id, updates)
        else:
            df = self._data["fraud_cases"]
            for k, v in updates.items():
                df.loc[df["case_id"] == case_id, k] = v
            self._data["fraud_cases"] = df
            self._sync_session("fraud_cases")

    def add_comment(self, case_id: str, author: str, comment_type: str, text: str, important: bool = False):
        new_row = {
            "comment_id": f"CMT{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "case_id": case_id,
            "author": author,
            "comment_type": comment_type,
            "comment_text": text,
            "created_at": datetime.now(),
            "important_flag": important,
        }
        self._append("case_comments", new_row)

    def add_history(self, case_id: str, action_type: str, old_value, new_value, action_by: str):
        new_row = {
            "history_id": f"HIS{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "case_id": case_id,
            "action_type": action_type,
            "old_value": str(old_value) if old_value is not None else None,
            "new_value": str(new_value) if new_value is not None else None,
            "action_by": action_by,
            "action_timestamp": datetime.now(),
        }
        self._append("case_history", new_row)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read(self, table: str) -> pd.DataFrame:
        # Session state takes priority (reflects in-session writes)
        key = f"_ds_{table}"
        if key in st.session_state:
            return st.session_state[key].copy()
        if self._use_delta:
            try:
                df = self._spark.table(f"{CATALOG}.{SCHEMA}.{table}").toPandas()
                st.session_state[key] = df
                return df.copy()
            except Exception:
                pass
        df = self._data.get(table, pd.DataFrame())
        st.session_state[key] = df
        return df.copy()

    def _append(self, table: str, row: dict):
        key = f"_ds_{table}"
        df = self._read(table)
        new_df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
        st.session_state[key] = new_df
        if self._use_delta:
            try:
                spark_df = self._spark.createDataFrame(pd.DataFrame([row]))
                spark_df.write.mode("append").saveAsTable(f"{CATALOG}.{SCHEMA}.{table}")
            except Exception:
                pass

    def _sync_session(self, table: str):
        key = f"_ds_{table}"
        st.session_state[key] = self._data[table]

    def _delta_update(self, table, key_col, key_val, updates):
        set_clause = ", ".join([f"{k} = '{v}'" for k, v in updates.items()])
        try:
            self._spark.sql(
                f"UPDATE {CATALOG}.{SCHEMA}.{table} SET {set_clause} WHERE {key_col} = '{key_val}'"
            )
        except Exception:
            pass

    @property
    def source(self) -> str:
        return "Delta Tables (Unity Catalog)" if self._use_delta else "Mock Data (in-memory)"
