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

def insert_transaction(user_id, date, transaction_type, desc, amount, category=None):
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
        
        # (!!! 수정 !!!) 'type' 변수명 충돌을 피하기 위해 'transaction_type'으로 변경
        cursor.execute(sql, (user_id, date, transaction_type, desc, amount, category))
        db.commit()
    except Exception as e:
        if db:
            db.rollback()
        # (!!! 수정 !!!) 'type' 변수명 충돌을 피하기 위해 __builtins__ 사용
        print(f"[INSERT LEDGER ERROR] {__builtins__.type(e).__name__}: {e}")
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

def update_transaction(trans_id, user_id, date, type, desc, amount):
    """ (신규) ID와 일치하는 거래 내역을 수정합니다. """
    db = None
    cursor = None
    try:
        db = db_connector() 
        cursor = db.cursor()
        
        # (중요) user_id까지 확인해야 다른 사람의 가계부를 수정할 수 없습니다.
        sql = """
            UPDATE ledger 
            SET 
                date = %s, 
                type = %s, 
                description = %s,
                amount = %s
            WHERE 
                id = %s AND user_id = %s
        """
        
        # (참고) insert와 순서가 다름 (id, user_id가 WHERE절로 감)
        affected_rows = cursor.execute(sql, (date, type, desc, amount, trans_id, user_id))
        db.commit()

        if affected_rows == 0:
            raise Exception("수정 권한이 없거나 존재하지 않는 내역입니다.")
        
    except Exception as e:
        if db:
            db.rollback()
        # (중요) type(e)를 사용하기 위해, 함수 인자 type과 겹치지 않게 
        # print문 안에서 __builtins__.type()을 사용합니다.
        print(f"[UPDATE LEDGER ERROR] {__builtins__.type(e).__name__}: {e}")
        raise # 오류를 app.py로 다시 보냄
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

def select_transactions_by_date(user_id, date):
    """ (신규 - '날짜별 조회' 브랜치에서 가져옴) 특정 사용자의 특정 날짜의 거래 내역만 조회합니다. """
    db = None
    cursor = None
    
    try:
        db = db_connector() # 기존 DB 연결 함수
        
        # 결과를 딕셔너리로 받기 위해 DictCursor 사용
        cursor = db.cursor(pymysql.cursors.DictCursor) 
        
        sql = """
            SELECT id, user_id, date, type, description, amount, category 
            FROM ledger 
            WHERE user_id = %s AND date = %s
            ORDER BY id ASC
        """
        
        cursor.execute(sql, (user_id, date))
        results = cursor.fetchall()
        return results
        
    except Exception as e:
        # (!!! 수정 !!!) 'type' 변수명 충돌을 피하기 위해 __builtins__ 사용
        print(f"[SELECT BY DATE ERROR] {__builtins__.type(e).__name__}: {e}")
        return [] # 오류 시 빈 리스트 반환
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()