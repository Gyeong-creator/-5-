import re
import sqlite3

DB_PATH = "users.db"

def is_valid_password(password: str) -> bool:
    """비밀번호 유효성 검사 : 
    - 8자 이상
    - 영문 1개 이상 포함
    - 숫자 1개 이상 포함
    - 특수문자 1개 이상 포함
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-za-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[A-Za-z0-9]", password):
        return False
    return True

def is_duplicate_user_id(user_id: str) -> bool:
    """user_id가 이미 존재하면 True"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def is_duplicate_user_name(user_name: str) -> bool:
    """user_name이 이미 존재하면 True"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_name = ?", (user_name,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists