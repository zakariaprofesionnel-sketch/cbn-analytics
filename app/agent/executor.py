"""Safe executor and persistence for Agent IA CBN decisions."""

from __future__ import annotations

import os
import sys
from datetime import datetime
from typing import Dict, Any

import pandas as pd
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import BASE_DIR, DB_URL  # noqa: E402


CSV_LOG_PATH = os.path.join(BASE_DIR, "data", "processed", "agent_decisions_log.csv")


def _ensure_sql_table(engine) -> None:
    ddl = """
    CREATE TABLE IF NOT EXISTS agent_action_log (
        id SERIAL PRIMARY KEY,
        ts TIMESTAMP NOT NULL,
        recommendation_id VARCHAR(120) NOT NULL,
        decision VARCHAR(20) NOT NULL,
        user_label VARCHAR(120),
        execution_status VARCHAR(30) NOT NULL,
        payload_json TEXT
    )
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))


def _log_to_sql(entry: Dict[str, Any]) -> bool:
    try:
        engine = create_engine(DB_URL)
        _ensure_sql_table(engine)
        insert_sql = text(
            """
            INSERT INTO agent_action_log (
                ts, recommendation_id, decision, user_label, execution_status, payload_json
            ) VALUES (
                :ts, :recommendation_id, :decision, :user_label, :execution_status, :payload_json
            )
            """
        )
        with engine.begin() as conn:
            conn.execute(insert_sql, entry)
        engine.dispose()
        return True
    except Exception:
        return False


def _log_to_csv(entry: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(CSV_LOG_PATH), exist_ok=True)
    df_new = pd.DataFrame([entry])
    if os.path.exists(CSV_LOG_PATH):
        df_old = pd.read_csv(CSV_LOG_PATH)
        df_out = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_out = df_new
    df_out.to_csv(CSV_LOG_PATH, index=False)


def record_decision(
    recommendation: Dict[str, Any],
    decision: str,
    user_label: str = "analyste_cbn",
) -> Dict[str, Any]:
    """Record validated/rejected recommendation in SQL + CSV backup."""
    entry = {
        "ts": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "recommendation_id": recommendation.get("id", "unknown"),
        "decision": decision,
        "user_label": user_label,
        "execution_status": "simulated",
        "payload_json": str(recommendation),
    }
    saved_in_sql = _log_to_sql(entry)
    # Keep a local audit backup even when SQL insert succeeds.
    _log_to_csv(entry)

    return {
        "status": "ok",
        "stored_in": "sql+csv" if saved_in_sql else "csv_only",
        "sql_saved": saved_in_sql,
        "entry": entry,
    }


def load_decision_history(limit: int = 200) -> pd.DataFrame:
    """Load history from SQL when available; fallback to CSV otherwise."""
    try:
        engine = create_engine(DB_URL)
        query = text(
            """
            SELECT ts, recommendation_id, decision, user_label, execution_status, payload_json
            FROM agent_action_log
            ORDER BY ts DESC
            LIMIT :limit
            """
        )
        df = pd.read_sql(query, engine, params={"limit": limit})
        engine.dispose()
        if not df.empty:
            return df
    except Exception:
        pass

    if os.path.exists(CSV_LOG_PATH):
        df_csv = pd.read_csv(CSV_LOG_PATH)
        return df_csv.tail(limit).iloc[::-1].reset_index(drop=True)

    return pd.DataFrame(
        columns=["ts", "recommendation_id", "decision", "user_label", "execution_status", "payload_json"]
    )

