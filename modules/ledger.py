import pymysql
from .user import db_connector # user.py에서 db_connector를 가져옴
from datetime import timedelta, date

# 특정 유저의 모든 거래 내역을 조회
def select_ledger_by_user(user_id):
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

# 해당 월의 지출 합계
def select_month_ledger_by_user(user_id, year, month, days, start, end):
    db = None
    cur = None
    try:
        db = db_connector()
        cur = db.cursor(pymysql.cursors.DictCursor)
        sql = """
            SELECT DATE(date) AS d,
                   SUM(CASE WHEN type='출금' THEN amount ELSE 0 END) AS spend
            FROM ledger
            WHERE user_id = %s AND date >= %s AND date < %s
            GROUP BY DATE(date)
            ORDER BY d
        """
        cur.execute(sql, (user_id, start, end))
        rows = cur.fetchall()
        by_day = {r['d']: int(r['spend'] or 0) for r in rows}

        labels = [f"{i}일" for i in range(1, days + 1)]
        cumulative = []
        running = 0
        for day in range(1, days + 1):
            d = date(year, month, day)
            running += by_day.get(d, 0)
            cumulative.append(running)

        return {'labels': labels, 'thisMonth': cumulative}
    finally:
        if cur: cur.close()
        if db: db.close()


# 해당 월의 지출/수입 합계
def select_month_daily_spend_income(user_id, start, end, year, month, days):
    db = None
    cur = None
    try:
        db = db_connector()
        cur = db.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT DATE(date) AS d,
                   SUM(CASE WHEN type = '입금'  THEN amount ELSE 0 END) AS income,
                   SUM(CASE WHEN type = '출금'  THEN amount ELSE 0 END) AS spend,
                   SUM(CASE WHEN type='출금' AND pay='카드'      THEN amount ELSE 0 END) AS card,
                   SUM(CASE WHEN type='출금' AND pay='계좌이체'  THEN amount ELSE 0 END) AS transfer,
                   SUM(CASE WHEN type='출금' AND pay NOT IN ('카드','계좌이체') THEN amount ELSE 0 END) AS other
            FROM ledger
            WHERE user_id = %s AND date >= %s AND date < %s
            GROUP BY DATE(date)
            ORDER BY d
        """
        cur.execute(sql, (user_id, start, end))
        rows = cur.fetchall()

        # 날짜별 합계를 맵으로 구성
        income_by_day   = {}
        spend_by_day    = {}
        card_by_day     = {}
        transfer_by_day = {}
        other_by_day    = {}
        for r in rows:
            d = r['d']              # datetime.date
            income_by_day[d]   = int(r['income']   or 0)
            spend_by_day[d]    = int(r['spend']    or 0)
            card_by_day[d]     = int(r['card']     or 0)
            transfer_by_day[d] = int(r['transfer'] or 0)
            other_by_day[d]    = int(r['other']    or 0)

        # 1일~말일까지 누적 생성 (거래 없는 날은 직전 누적 유지)
        labels       = [f"{i}일" for i in range(1, days+1)]
        cumIncome    = []
        cumSpend     = []
        cumCard      = []
        cumTransfer  = []
        cumOther     = []

        run_inc = run_spd = run_card = run_tr = run_oth = 0
        for day in range(1, days+1):
            d = date(year, month, day)
            run_inc += income_by_day.get(d, 0)
            run_spd += spend_by_day.get(d, 0)
            run_card += card_by_day.get(d, 0)
            run_tr   += transfer_by_day.get(d, 0)
            run_oth  += other_by_day.get(d, 0)

            cumIncome.append(run_inc)
            cumSpend.append(run_spd)
            cumCard.append(run_card)
            cumTransfer.append(run_tr)
            cumOther.append(run_oth)

        return {
            'labels': labels,
            'cumIncome':   cumIncome,
            'cumSpend':    cumSpend,
            'cumCard':     cumCard,
            'cumTransfer': cumTransfer,
            'cumOther':    cumOther,

            'totalIncome': run_inc,
            'totalSpend':  run_spd,
            'totalCard': run_card,
            'totalTransfer': run_tr,
            'totalOther':  run_oth,
        }
    finally:
        if cur: cur.close()
        if db: db.close()


# 이번 달 지출 카테고리 합계/비중
def select_month_category_spend(user_id, start, end):
    db = None
    cur = None
    try:
        db = db_connector()
        cur = db.cursor(pymysql.cursors.DictCursor)

        sql = """
            SELECT
              COALESCE(NULLIF(TRIM(category), ''), '기타') AS cat,
              SUM(
                CASE
                  WHEN TRIM(LOWER(type)) <> '입금'
                  THEN CAST(REPLACE(amount, ',', '') AS SIGNED)
                  ELSE 0
                END
              ) AS spend
            FROM ledger
            WHERE user_id = %s
              AND date >= %s AND date < %s
            GROUP BY cat
            HAVING spend > 0
            ORDER BY spend DESC
        """
        cur.execute(sql, (user_id, start, end))
        rows = cur.fetchall()  # [{'cat': '식비', 'spend': 12345}, ...]

        total = sum(int(r['spend'] or 0) for r in rows) or 0
        items = []
        for r in rows:
            amt = int(r['spend'] or 0)
            pct = (amt / total * 100.0) if total > 0 else 0.0
            items.append({
                'category': r['cat'],
                'amount': amt,
                'pct': round(pct, 1)  # 1자리 소수
            })

        return { 'total': total, 'items': items }
    finally:
        if cur: cur.close()
        if db: db.close()
