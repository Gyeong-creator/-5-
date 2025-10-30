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

def select_ledger_by_user(user_id):
    """
    특정 유저의 모든 거래 내역을 조회합니다.
    """
    db = None
    cursor = None
    
    try:
        db = db_connector()
        cursor = db.cursor(pymysql.cursors.DictCursor) 
    
        sql = """
            SELECT id, user_id, date, type, description, amount, category 
            FROM ledger 
            WHERE user_id = %s 
            ORDER BY date DESC
        """
        
        cursor.execute(sql, (user_id,))
        results = cursor.fetchall()
        return results

    except Exception as e:
        print(f"[SELECT LEDGER ERROR] {type(e).__name__}: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()