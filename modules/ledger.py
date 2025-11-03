import pymysql
from .user import db_connector # user.py에서 db_connector를 가져옴

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

def insert_transaction(user_id, date, type, desc, amount, category=None):
    """(추가) 새로운 거래 내역을 DB에 추가합니다."""
    db = None
    cursor = None
    try:
        db = db_connector()
        cursor = db.cursor()
        sql = """
            INSERT INTO ledger (user_id, date, type, description, amount, category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        # (DB 컬럼명이 'description'이므로, 'desc' 변수를 description 컬럼에 삽입)
        cursor.execute(sql, (user_id, date, type, desc, amount, category))
        db.commit()
    except Exception as e:
        if db:
            db.rollback()
        print(f"[INSERT LEDGER ERROR] {type(e).__name__}: {e}")
        raise # 오류를 app.py로 전달
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def delete_transaction_by_id(transaction_id, user_id):
    """(추가) 특정 거래 내역을 DB에서 삭제합니다."""
    db = None
    cursor = None
    try:
        db = db_connector()
        cursor = db.cursor()
        # 보안: id와 user_id가 모두 일치하는 항목만 삭제
        sql = "DELETE FROM ledger WHERE id = %s AND user_id = %s"
        affected_rows = cursor.execute(sql, (transaction_id, user_id))
        db.commit()
        
        if affected_rows == 0:
            raise Exception("삭제 권한이 없거나 존재하지 않는 내역입니다.")
    except Exception as e:
        if db:
            db.rollback()
        print(f"[DELETE LEDGER ERROR] {type(e).__name__}: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()