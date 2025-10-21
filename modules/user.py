import pymysql
from . import config

def db_connector():
    try:
        conn = pymysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.passwd,
            db=config.db,
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"[DB CONNECT ERROR] {type(e).__name__}: {e}")
        raise

def select_user_info(id, pw):
    db = db_connector()
    cur = db.cursor(pymysql.cursors.DictCursor)
    try:
        cur.execute("SELECT * FROM user WHERE id=%s AND password=%s", (id, pw))
        rows = cur.fetchall()
        return rows or None
    finally:
        cur.close()
        db.close()
