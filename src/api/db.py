from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime

import pandas as pd

from src.api.config import settings


CLAIMS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS submitted_claims (
    claim_id TEXT PRIMARY KEY,
    claimant_id TEXT NOT NULL,
    claimant_name TEXT NOT NULL,
    claimant_email TEXT NOT NULL,
    policy_type TEXT NOT NULL,
    coverage_tier TEXT NOT NULL,
    policy_start_date TEXT NOT NULL,
    claim_date TEXT NOT NULL,
    claim_submission_timestamp TEXT NOT NULL,
    claim_channel TEXT NOT NULL,
    claimant_age_band TEXT NOT NULL,
    claimant_tenure_days INTEGER NOT NULL,
    postal_region TEXT NOT NULL,
    item_category TEXT NOT NULL,
    item_purchase_date TEXT NOT NULL,
    claimed_incident_date TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    claim_amount_gbp REAL NOT NULL,
    estimated_item_value_gbp REAL NOT NULL,
    claim_amount_vs_item_value_ratio REAL NOT NULL,
    prior_claims_count INTEGER NOT NULL,
    claims_last_12_months INTEGER NOT NULL,
    approved_claims_last_24_months INTEGER NOT NULL,
    denied_claims_last_24_months INTEGER NOT NULL,
    days_since_last_claim INTEGER NOT NULL,
    days_since_policy_start INTEGER NOT NULL,
    premium_payment_missed_last_12_months INTEGER NOT NULL,
    recent_high_value_purchase_flag INTEGER NOT NULL,
    unusual_spend_spike_flag INTEGER NOT NULL,
    account_login_location_change_flag INTEGER NOT NULL,
    multiple_devices_last_7_days_flag INTEGER NOT NULL,
    address_change_last_30_days_flag INTEGER NOT NULL,
    phone_change_last_30_days_flag INTEGER NOT NULL,
    bank_detail_change_last_30_days_flag INTEGER NOT NULL,
    late_night_submission_flag INTEGER NOT NULL,
    weekend_submission_flag INTEGER NOT NULL,
    receipt_present_flag INTEGER NOT NULL,
    receipt_mismatch_flag INTEGER NOT NULL,
    duplicate_receipt_flag INTEGER NOT NULL,
    image_tamper_flag INTEGER NOT NULL,
    evidence_name TEXT NOT NULL DEFAULT '',
    evidence_media_type TEXT NOT NULL DEFAULT '',
    evidence_storage_path TEXT NOT NULL DEFAULT '',
    evidence_sha256 TEXT NOT NULL DEFAULT '',
    cv_signal_summary TEXT NOT NULL DEFAULT '',
    email_language_risk_score REAL NOT NULL,
    behavioural_risk_score REAL NOT NULL,
    document_risk_score REAL NOT NULL,
    overall_risk_label TEXT NOT NULL,
    manual_review_outcome TEXT NOT NULL
);
"""

EVIDENCE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS evidence_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stored_filename TEXT NOT NULL,
    media_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    evidence_sha256 TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
"""

USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS app_users (
    username TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_salt TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1
);
"""


def get_connection() -> sqlite3.Connection:
    settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database() -> None:
    with closing(get_connection()) as connection:
        connection.execute(CLAIMS_TABLE_SQL)
        connection.execute(EVIDENCE_TABLE_SQL)
        connection.execute(USERS_TABLE_SQL)
        connection.commit()


def database_ready() -> bool:
    try:
        with closing(get_connection()) as connection:
            connection.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def insert_submitted_claim(record: dict) -> None:
    with closing(get_connection()) as connection:
        columns = list(record.keys())
        placeholders = ", ".join(["?"] * len(columns))
        connection.execute(
            f"INSERT INTO submitted_claims ({', '.join(columns)}) VALUES ({placeholders})",
            [record[column] for column in columns],
        )
        connection.commit()


def fetch_submitted_claims_dataframe() -> pd.DataFrame:
    with closing(get_connection()) as connection:
        if not _table_exists(connection, "submitted_claims"):
            return pd.DataFrame()
        dataframe = pd.read_sql_query(
            "SELECT * FROM submitted_claims ORDER BY claim_submission_timestamp DESC",
            connection,
        )
    return dataframe


def evidence_hash_exists(file_hash: str) -> bool:
    with closing(get_connection()) as connection:
        if not _table_exists(connection, "evidence_files"):
            return False
        row = connection.execute(
            "SELECT 1 FROM evidence_files WHERE evidence_sha256 = ? LIMIT 1",
            (file_hash,),
        ).fetchone()
    return row is not None


def insert_evidence_file(*, stored_filename: str, media_type: str, storage_path: str, file_hash: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO evidence_files (
                stored_filename, media_type, storage_path, evidence_sha256, created_at
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (stored_filename, media_type, storage_path, file_hash, datetime.now().isoformat(timespec="seconds")),
        )
        connection.commit()


def upsert_user(*, username: str, full_name: str, role: str, password_salt: str, password_hash: str) -> None:
    with closing(get_connection()) as connection:
        connection.execute(
            """
            INSERT INTO app_users (username, full_name, role, password_salt, password_hash, is_active)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(username) DO UPDATE SET
                full_name = excluded.full_name,
                role = excluded.role,
                password_salt = excluded.password_salt,
                password_hash = excluded.password_hash,
                is_active = 1
            """,
            (username, full_name, role, password_salt, password_hash),
        )
        connection.commit()


def fetch_user(username: str) -> sqlite3.Row | None:
    with closing(get_connection()) as connection:
        if not _table_exists(connection, "app_users"):
            return None
        row = connection.execute(
            """
            SELECT username, full_name, role, password_salt, password_hash, is_active
            FROM app_users
            WHERE username = ?
            LIMIT 1
            """,
            (username,),
        ).fetchone()
    return row


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?
        LIMIT 1
        """,
        (table_name,),
    ).fetchone()
    return row is not None
