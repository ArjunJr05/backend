import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from app.db.models import QueueStatus, TeamInDB, QueueEntry, EvaluationResult, LeaderboardEntry
from app.config import DATABASE_PATH, DATA_DIR

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            team_id TEXT PRIMARY KEY,
            team_name TEXT NOT NULL,
            endpoint_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue (
            team_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            position INTEGER,
            queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            failure_reason TEXT,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            team_id TEXT PRIMARY KEY,
            accuracy REAL NOT NULL,
            f1_score REAL NOT NULL,
            latency_ms REAL NOT NULL,
            evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (team_id) REFERENCES teams(team_id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def add_team(team_id: str, team_name: str, endpoint_url: str) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO teams (team_id, team_name, endpoint_url) VALUES (?, ?, ?)",
            (team_id, team_name, endpoint_url)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE teams SET team_name = ?, endpoint_url = ? WHERE team_id = ?",
            (team_name, endpoint_url, team_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()

def add_to_queue(team_id: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(position) FROM queue WHERE status = ?", (QueueStatus.QUEUED.value,))
    max_pos = cursor.fetchone()[0]
    position = (max_pos or 0) + 1
    
    try:
        cursor.execute(
            "INSERT INTO queue (team_id, status, position) VALUES (?, ?, ?)",
            (team_id, QueueStatus.QUEUED.value, position)
        )
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE queue SET status = ?, position = ?, queued_at = CURRENT_TIMESTAMP, failure_reason = NULL WHERE team_id = ?",
            (QueueStatus.QUEUED.value, position, team_id)
        )
    
    conn.commit()
    conn.close()
    return position

def get_queue_status(team_id: str) -> Optional[QueueEntry]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT team_id, status, position, queued_at, failure_reason FROM queue WHERE team_id = ?",
        (team_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return QueueEntry(
            team_id=row[0],
            status=QueueStatus(row[1]),
            position=row[2],
            queued_at=datetime.fromisoformat(row[3]),
            failure_reason=row[4]
        )
    return None

def get_next_in_queue() -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT COUNT(*) FROM queue WHERE status = ?",
        (QueueStatus.EVALUATING.value,)
    )
    if cursor.fetchone()[0] > 0:
        conn.close()
        return None
    
    cursor.execute(
        "SELECT team_id FROM queue WHERE status = ? ORDER BY position ASC LIMIT 1",
        (QueueStatus.QUEUED.value,)
    )
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None

def update_queue_status(team_id: str, status: QueueStatus, failure_reason: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE queue SET status = ?, failure_reason = ? WHERE team_id = ?",
        (status.value, failure_reason, team_id)
    )
    
    conn.commit()
    conn.close()

def save_result(team_id: str, accuracy: float, f1_score: float, latency_ms: float):
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO results (team_id, accuracy, f1_score, latency_ms) VALUES (?, ?, ?, ?)",
            (team_id, accuracy, f1_score, latency_ms)
        )
    except sqlite3.IntegrityError:
        cursor.execute(
            "UPDATE results SET accuracy = ?, f1_score = ?, latency_ms = ?, evaluated_at = CURRENT_TIMESTAMP WHERE team_id = ?",
            (accuracy, f1_score, latency_ms, team_id)
        )
    
    conn.commit()
    conn.close()

def get_leaderboard() -> List[LeaderboardEntry]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT t.team_id, t.team_name, r.accuracy, r.f1_score, r.latency_ms, r.evaluated_at
        FROM results r
        JOIN teams t ON r.team_id = t.team_id
        ORDER BY r.accuracy DESC, r.f1_score DESC, r.evaluated_at ASC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    leaderboard = []
    for idx, row in enumerate(rows, 1):
        leaderboard.append(LeaderboardEntry(
            rank=idx,
            team_id=row[0],
            team_name=row[1],
            accuracy=row[2],
            f1_score=row[3],
            latency_ms=row[4],
            evaluated_at=datetime.fromisoformat(row[5])
        ))
    
    return leaderboard

def get_team_result(team_id: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT team_name, endpoint_url FROM teams WHERE team_id = ?",
        (team_id,)
    )
    team_row = cursor.fetchone()
    
    if not team_row:
        conn.close()
        return None
    
    cursor.execute(
        "SELECT status, failure_reason FROM queue WHERE team_id = ?",
        (team_id,)
    )
    queue_row = cursor.fetchone()
    
    cursor.execute(
        "SELECT accuracy, f1_score, latency_ms, evaluated_at FROM results WHERE team_id = ?",
        (team_id,)
    )
    result_row = cursor.fetchone()
    
    conn.close()
    
    result = {
        "team_id": team_id,
        "team_name": team_row[0],
        "status": queue_row[0] if queue_row else None,
        "accuracy": result_row[0] if result_row else None,
        "f1_score": result_row[1] if result_row else None,
        "latency_ms": result_row[2] if result_row else None,
        "evaluated_at": datetime.fromisoformat(result_row[3]) if result_row else None,
    }
    
    if result["status"] == QueueStatus.COMPLETED.value and result_row:
        leaderboard = get_leaderboard()
        for entry in leaderboard:
            if entry.team_id == team_id:
                result["rank"] = entry.rank
                break
    
    return result

def get_team_endpoint(team_id: str) -> Optional[str]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT endpoint_url FROM teams WHERE team_id = ?", (team_id,))
    row = cursor.fetchone()
    conn.close()
    
    return row[0] if row else None
