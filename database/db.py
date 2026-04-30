import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "moneymate.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            currency TEXT DEFAULT 'USD',
            theme TEXT DEFAULT 'light',
            notifications INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income','expense')),
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            saved_amount REAL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# ── Users ──────────────────────────────────────

def register_user(name, username, email, password):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name,username,email,password) VALUES (?,?,?,?)",
            (name, username, email, password)
        )
        conn.commit()
        uid = c.lastrowid
        conn.close()
        return True, uid
    except sqlite3.IntegrityError as e:
        msg = "Username already taken." if "username" in str(e) else "Email already registered."
        return False, msg


def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_info(user_id, name=None, username=None, email=None, password=None):
    conn = get_connection()
    c = conn.cursor()
    if name:
        c.execute("UPDATE users SET name=? WHERE id=?", (name, user_id))
    if username:
        c.execute("UPDATE users SET username=? WHERE id=?", (username, user_id))
    if email:
        c.execute("UPDATE users SET email=? WHERE id=?", (email, user_id))
    if password:
        c.execute("UPDATE users SET password=? WHERE id=?", (password, user_id))
    conn.commit()
    conn.close()


def update_user_settings(user_id, currency=None, theme=None, notifications=None):
    conn = get_connection()
    c = conn.cursor()
    if currency:
        c.execute("UPDATE users SET currency=? WHERE id=?", (currency, user_id))
    if theme:
        c.execute("UPDATE users SET theme=? WHERE id=?", (theme, user_id))
    if notifications is not None:
        c.execute("UPDATE users SET notifications=? WHERE id=?", (notifications, user_id))
    conn.commit()
    conn.close()


# ── Transactions ───────────────────────────────

def add_transaction(user_id, t_type, amount, category, note=""):
    conn = get_connection()
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute(
        "INSERT INTO transactions (user_id,type,amount,category,note,date) VALUES (?,?,?,?,?,?)",
        (user_id, t_type, amount, category, note, date)
    )
    conn.commit()
    conn.close()


def get_transactions(user_id, limit=50):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_monthly_summary(user_id):
    conn = get_connection()
    c = conn.cursor()
    month = datetime.now().strftime("%Y-%m")
    c.execute("""
        SELECT type, SUM(amount) as total
        FROM transactions
        WHERE user_id=? AND date LIKE ?
        GROUP BY type
    """, (user_id, f"{month}%"))
    result = {"income": 0.0, "expense": 0.0}
    for row in c.fetchall():
        result[row["type"]] = row["total"]
    conn.close()
    return result


def delete_transaction(tid):
    conn = get_connection()
    conn.execute("DELETE FROM transactions WHERE id=?", (tid,))
    conn.commit()
    conn.close()


# ── Goals ──────────────────────────────────────

def add_goal(user_id, name, target_amount):
    conn = get_connection()
    conn.execute(
        "INSERT INTO goals (user_id,name,target_amount) VALUES (?,?,?)",
        (user_id, name, target_amount)
    )
    conn.commit()
    conn.close()


def get_goals(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM goals WHERE user_id=?", (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def update_goal_saved(goal_id, amount):
    conn = get_connection()
    conn.execute(
        "UPDATE goals SET saved_amount=saved_amount+? WHERE id=?",
        (amount, goal_id)
    )
    conn.commit()
    conn.close()


def delete_goal(goal_id):
    conn = get_connection()
    conn.execute("DELETE FROM goals WHERE id=?", (goal_id,))
    conn.commit()
    conn.close()