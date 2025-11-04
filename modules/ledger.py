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

def select_transactions_by_date(user_id, selected_date):
    """
    [새 기능] 날짜별 조회: 특정 유저의 '특정 날짜' 거래 내역만 조회합니다.
    """
    db = None
    cursor = None
    try:
        db = db_connector()
        cursor = db.cursor(pymysql.cursors.DictCursor) 
    
        sql = """
            SELECT 
                id, 
                user_id, 
                date, 
                type, 
                description,
                amount, 
                category 
            FROM ledger 
            WHERE user_id = %s AND DATE(date) = %s  -- DATE() 함수로 시간 부분 제외하고 날짜만 비교
            ORDER BY id DESC
        """
        
        cursor.execute(sql, (user_id, selected_date))
        results = cursor.fetchall()
        return results

    except Exception as e:
        print(f"[SELECT LEDGER BY DATE ERROR] {type(e).__name__}: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()