import os
import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_DIR = ROOT / "storage" / "db"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "nda_history.db"


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a parameterized SQLite database connection."""
    target_path = db_path or DEFAULT_DB_PATH
    target_dir = target_path.parent
    target_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize database tables safely (idempotent)."""
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_history (
                    document_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_timestamp TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    character_count INTEGER NOT NULL,
                    word_count INTEGER NOT NULL,
                    total_clauses INTEGER NOT NULL,
                    high_risk_clause_count INTEGER NOT NULL,
                    medium_risk_clause_count INTEGER NOT NULL,
                    model_choice TEXT NOT NULL,
                    threshold REAL NOT NULL,
                    overall_risk_index REAL NOT NULL,
                    risk_status TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    advice TEXT NOT NULL,
                    detected_categories_json TEXT NOT NULL,
                    result_json TEXT NOT NULL
                )
            """)
    finally:
        conn.close()


def save_document_analysis(
    analysis_dict: Dict[str, Any],
    model_choice: str = "legal_roberta",
    threshold: float = 0.60,
    db_path: Optional[Path] = None,
) -> None:
    """Save completed analysis result into database history."""
    init_db(db_path)
    conn = get_db_connection(db_path)

    timestamp = datetime.now(timezone.utc).isoformat()
    document_id = analysis_dict["document_id"]
    filename = analysis_dict["filename"]
    page_count = analysis_dict.get("page_count", 0)
    character_count = analysis_dict.get("character_count", 0)
    word_count = analysis_dict.get("word_count", 0)
    total_clauses = analysis_dict.get("total_clauses", 0)
    high_risk_clause_count = analysis_dict.get("high_risk_clause_count", 0)
    medium_risk_clause_count = analysis_dict.get("medium_risk_clause_count", 0)
    overall_risk_index = analysis_dict.get("overall_risk_index", 0.0)
    risk_status = analysis_dict.get("risk_status", "UNKNOWN")
    recommendation = analysis_dict.get("recommendation", "")
    advice = analysis_dict.get("advice", "")
    detected_categories = analysis_dict.get("detected_categories", [])

    detected_json = json.dumps(detected_categories)
    result_json = json.dumps(analysis_dict)

    try:
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO document_history (
                    document_id, filename, upload_timestamp, page_count,
                    character_count, word_count, total_clauses,
                    high_risk_clause_count, medium_risk_clause_count,
                    model_choice, threshold, overall_risk_index,
                    risk_status, recommendation, advice,
                    detected_categories_json, result_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_id, filename, timestamp, page_count,
                character_count, word_count, total_clauses,
                high_risk_clause_count, medium_risk_clause_count,
                model_choice, threshold, overall_risk_index,
                risk_status, recommendation, advice,
                detected_json, result_json
            ))
    finally:
        conn.close()


def list_document_analyses(
    skip: int = 0,
    limit: int = 20,
    db_path: Optional[Path] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    List recent document analyses with pagination.
    Returns tuple of (summary_list, total_count).
    """
    init_db(db_path)
    conn = get_db_connection(db_path)

    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM document_history")
        total_count = cur.fetchone()[0]

        cur.execute("""
            SELECT document_id, filename, upload_timestamp, page_count,
                   total_clauses, high_risk_clause_count, medium_risk_clause_count,
                   model_choice, threshold, overall_risk_index, risk_status,
                   recommendation, detected_categories_json
            FROM document_history
            ORDER BY upload_timestamp DESC
            LIMIT ? OFFSET ?
        """, (limit, skip))

        rows = cur.fetchall()
        results = []
        for r in rows:
            item = dict(r)
            item["detected_categories"] = json.loads(item.pop("detected_categories_json"))
            results.append(item)

        return results, total_count
    finally:
        conn.close()


def get_document_analysis(
    document_id: str,
    db_path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """Retrieve full document analysis result by ID."""
    init_db(db_path)
    conn = get_db_connection(db_path)

    try:
        cur = conn.cursor()
        cur.execute("SELECT result_json FROM document_history WHERE document_id = ?", (document_id,))
        row = cur.fetchone()
        if not row:
            return None
        return json.loads(row["result_json"])
    finally:
        conn.close()
