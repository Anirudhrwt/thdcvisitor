"""
database.py
------------
Every database action (create tables, add admin, remove admin,
save visitor, fetch visitors, check login, update last login)
lives in this one file, kept separate from the website routes
in app.py.

Uses Python's built-in sqlite3 module, so no extra installs
are needed for the database itself.
"""

import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

import config


def get_connection():
    conn = sqlite3.connect(config.DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist, and create the head admin
    account only if it doesn't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,              -- 'head_admin' or 'admin'
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            reason TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            visit_time TEXT NOT NULL,
            pass_id TEXT
        )
    """)
    conn.commit()

    # Migration: older databases created before the Pass ID feature
    # won't have this column yet - add it if missing, without touching
    # any existing visitor rows.
    existing_columns = [row["name"] for row in cur.execute("PRAGMA table_info(visitors)")]
    if "pass_id" not in existing_columns:
        cur.execute("ALTER TABLE visitors ADD COLUMN pass_id TEXT")
        conn.commit()

    # Holds a visitor's details temporarily while their mobile
    # number is being OTP-verified. Only moved into the real
    # 'visitors' table once the correct OTP is entered.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pending_visitors (
            phone TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            reason TEXT NOT NULL,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    # Records EVERY admin login (not just the latest), so the head
    # admin can see a full login history for each admin.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            login_time TEXT NOT NULL
        )
    """)
    conn.commit()

    # Create head admin only once, using the values from config.py
    cur.execute("SELECT * FROM users WHERE role = 'head_admin'")
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (
                config.HEAD_ADMIN_USERNAME,
                generate_password_hash(config.HEAD_ADMIN_PASSWORD),
                "head_admin",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()

    conn.close()


# ---------- Visitor functions ----------

def add_visitor(name, reason, email, phone):
    visit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO visitors (name, reason, email, phone, visit_time) VALUES (?, ?, ?, ?, ?)",
        (name, reason, email, phone, visit_time),
    )
    conn.commit()
    visitor_id = cur.lastrowid

    # Pass ID depends on the row's own id, so it's generated right
    # after inserting, then saved back onto that same row.
    pass_id = f"THDC-{visitor_id:05d}"
    conn.execute("UPDATE visitors SET pass_id = ? WHERE id = ?", (pass_id, visitor_id))
    conn.commit()
    conn.close()

    return visitor_id, visit_time, pass_id


def get_all_visitors():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM visitors ORDER BY id DESC").fetchall()
    conn.close()
    return rows


# ---------- Pending visitor (OTP) functions ----------

def save_pending_visitor(name, reason, email, phone, otp, expires_at):
    """Stores the form details + OTP while waiting for mobile verification.
    Re-submitting the same phone number simply replaces the old pending entry."""
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO pending_visitors (phone, name, reason, email, otp, expires_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (phone, name, reason, email, otp, expires_at),
    )
    conn.commit()
    conn.close()


def get_pending_visitor(phone):
    conn = get_connection()
    row = conn.execute("SELECT * FROM pending_visitors WHERE phone = ?", (phone,)).fetchone()
    conn.close()
    return row


def delete_pending_visitor(phone):
    conn = get_connection()
    conn.execute("DELETE FROM pending_visitors WHERE phone = ?", (phone,))
    conn.commit()
    conn.close()


# ---------- User (admin) functions ----------

def get_user_by_username(username):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def check_login(username, password):
    user = get_user_by_username(username)
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def update_last_login(username):
    conn = get_connection()
    conn.execute(
        "UPDATE users SET last_login = ? WHERE username = ?",
        (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), username),
    )
    conn.commit()
    conn.close()


def log_login(username, role):
    """Records this login as a new row, so a full history builds up
    over time (unlike last_login on the users table, which only
    keeps the most recent one)."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO login_logs (username, role, login_time) VALUES (?, ?, ?)",
        (username, role, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()


def get_all_login_logs():
    """Every login made by ANYONE - head admin and admins - most recent
    first. Used on the dedicated Login Activity page (head admin only)."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM login_logs ORDER BY id DESC").fetchall()
    conn.close()
    return rows


def get_all_admins():
    """Used by the head admin to see every admin's login details."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM users WHERE role = 'admin' ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return rows


def add_admin(username, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (
                username,
                generate_password_hash(password),
                "admin",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # username already taken
    conn.close()
    return success


def remove_admin(user_id):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ? AND role = 'admin'", (user_id,))
    conn.commit()
    conn.close()
