import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, List

DB_PATH = "pocketwise.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # User Profile Table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (
                     user_id      TEXT PRIMARY KEY,
                     profile_json TEXT
                 )''')

    # Expenses/Logs Table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (
                     id          INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id     TEXT,
                     description TEXT,
                     amount      REAL,
                     category    TEXT,
                     context     TEXT,
                     timestamp   TEXT
                 )''')

    # Plans Table
    c.execute('''CREATE TABLE IF NOT EXISTS plans
                 (
                     id          INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id     TEXT,
                     plan_type   TEXT,
                     content     TEXT,
                     start_date  TEXT,
                     goal_amount REAL,
                     stages_amount  REAL,
                     status      TEXT
                 )''')

    conn.commit()
    conn.close()


# --- User Operations ---

def get_user_profile(user_id: str) -> Dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT profile_json FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return json.loads(row[0])
    else:
        # Default profile if new user
        default_profile = {
            "income": 0,
            "monthly_budget": 0,
            "saving": 0,
            "personality_tags": [],
            "current_mood": "neutral"
        }
        update_user_profile(user_id, default_profile)
        return default_profile


def update_user_profile(user_id: str, updates: Dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get existing first to merge
    c.execute("SELECT profile_json FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()

    if row:
        current_profile = json.loads(row[0])
        current_profile.update(updates)
    else:
        current_profile = updates

    c.execute("INSERT OR REPLACE INTO users (user_id, profile_json) VALUES (?, ?)",
              (user_id, json.dumps(current_profile)))
    conn.commit()
    conn.close()
    return current_profile


# --- Expense Operations ---

def add_expense(user_id: str, description: str, amount: float, category: str,
                context: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    timestamp = datetime.now().isoformat()
    c.execute(
        "INSERT INTO expenses (user_id, description, amount, category, context, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, description, amount, category, context, timestamp))
    conn.commit()
    conn.close()


def get_recent_expenses(user_id: str, limit: int = 5) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT ?",
              (user_id, limit))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# --- Plan Operations ---

def add_plan(user_id: str, plan_type: str, content: str, start_date: str,
             stages_amount: float = None, goal_amount: float = None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO plans (user_id, plan_type, content, start_date, goal_amount, stages_amount, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, plan_type, content, start_date, stages_amount, goal_amount, "active"))
    conn.commit()
    conn.close()


def update_plan(plan_id: int, user_id: str, plan_type: str = None, content: str = None,
                start_date: str = None, goal_amount: float = None, stages_amount: float = None, status: str = None) -> bool:
    """更新计划，支持部分字段更新"""
    # 构建更新字段字典，只包含非None值
    updates = {}
    if plan_type is not None:
        updates['plan_type'] = plan_type
    if content is not None:
        updates['content'] = content
    if start_date is not None:
        updates['start_date'] = start_date
    if goal_amount is not None:
        updates['goal_amount'] = goal_amount
    if stages_amount is not None:
        updates['stages_amount'] = stages_amount
    if status is not None:
        updates['status'] = status

    if not updates:
        return False

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 动态构建SET子句
    set_clause = ", ".join(f"{key}=?" for key in updates.keys())
    sql = f"UPDATE plans SET {set_clause} WHERE id=? AND user_id=?"

    # 构建参数列表
    params = list(updates.values()) + [plan_id, user_id]

    c.execute(sql, params)
    conn.commit()
    conn.close()
    return c.rowcount > 0


def delete_plan(plan_id: int, user_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM plans WHERE id=? AND user_id=?", (plan_id, user_id))
    conn.commit()
    conn.close()
    return c.rowcount > 0


def get_active_plans(user_id: str) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM plans WHERE user_id = ? AND status = 'active'", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stage_plan(user_id: str) -> dict:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT stages_amount FROM plans WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    stages_amounts = {}
    n = 1
    for row in rows:
        stages_amounts[f"计划{n}:"] = row
        n += 1
    return stages_amounts
