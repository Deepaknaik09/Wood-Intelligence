"""
Authentication and User Management Module for Wood Intelligence
Provides secure user signup, login, session management, and inspector profiles
using a local SQLite database with salted PBKDF2-HMAC-SHA256 password hashing.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, Dict, Tuple, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.db")

INSPECTOR_ROLES = [
    "Timber Quality Inspector",
    "Master Joiner / Carpenter",
    "Structural Timber Engineer",
    "Lumber Procurement Manager",
    "Research Wood Botanist",
    "Industrial Mill Operator"
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes user table and pre-seeds a sample inspector account if empty."""
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
            """)
        
        # Check if table has any users; if not, seed default inspector
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        count = cur.fetchone()[0]
        if count == 0:
            register_user(
                username="inspector",
                password="timber123",
                full_name="Lead Inspector",
                role="Timber Quality Inspector"
            )
    finally:
        conn.close()

def _hash_password(password: str, salt: str) -> str:
    """Derives a key using PBKDF2 HMAC SHA-256."""
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    )
    return key.hex()

def register_user(username: str, password: str, full_name: str, role: str) -> Tuple[bool, str]:
    """Registers a new user account. Returns (success, message)."""
    username = username.strip().lower()
    full_name = full_name.strip()
    
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    if not full_name:
        return False, "Please enter your full name or inspector title."
    if role not in INSPECTOR_ROLES:
        role = INSPECTOR_ROLES[0]
        
    salt = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO users (username, password_hash, salt, full_name, role, created_at, last_login)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, pw_hash, salt, full_name, role, now, now))
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, f"Username '{username}' is already registered. Please choose another or log in."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Validates user credentials. Returns (user_dict, message)."""
    username = username.strip().lower()
    if not username or not password:
        return None, "Please provide both username and password."
        
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        if not row:
            return None, "Account not found with that username."
            
        salt = row["salt"]
        expected_hash = row["password_hash"]
        calc_hash = _hash_password(password, salt)
        
        # Constant-time comparison
        if secrets.compare_digest(expected_hash, calc_hash):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with conn:
                conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (now, row["id"]))
            
            user = {
                "id": row["id"],
                "username": row["username"],
                "full_name": row["full_name"],
                "role": row["role"],
                "created_at": row["created_at"],
                "last_login": now,
                "is_authenticated": True
            }
            return user, "Authentication successful."
        else:
            return None, "Invalid password."
    except Exception as e:
        return None, f"Authentication error: {str(e)}"
    finally:
        conn.close()

# Auto-initialize database on import
init_db()
