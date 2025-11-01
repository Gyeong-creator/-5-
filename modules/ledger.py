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


def select_recent_weeks(user_id, n_weeks: int):

    db = cur = None
    try:
        db = db_connector()
        cur = db.cursor(pymysql.cursors.DictCursor)

        sql = """
        WITH RECURSIVE seq(i) AS (
            SELECT 0
            UNION ALL
            SELECT i + 1 FROM seq WHERE i + 1 < %s   -- 0..(n_weeks-1)
        ),
        base AS (
            -- 이번 주 월요일(한국 기준: WEEKDAY()=0이 월)
            SELECT DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY) AS monday_this_week
        ),
        weeks AS (
            -- i=0: 이번 주, i=1: 지난 주 ...
            SELECT DATE_SUB(b.monday_this_week, INTERVAL s.i WEEK) AS week_start
            FROM base b
            JOIN seq  s
        ),
        agg AS (
            SELECT
                w.week_start,
                COALESCE(SUM(CASE
                    WHEN LOWER(TRIM(l.type)) IN ('입금','수입')
                    THEN CAST(REPLACE(l.amount, ',', '') AS SIGNED)
                    ELSE 0 END), 0) AS income,
                COALESCE(SUM(CASE
                    WHEN LOWER(TRIM(l.type)) IN ('출금','지출')
                    THEN CAST(REPLACE(l.amount, ',', '') AS SIGNED)
                    ELSE 0 END), 0) AS spend
            FROM weeks w
            LEFT JOIN ledger l
              ON l.user_id = %s
             AND l.date >= w.week_start
             AND l.date <  DATE_ADD(w.week_start, INTERVAL 7 DAY)
            GROUP BY w.week_start
        )
        SELECT
            DATE_FORMAT(week_start, '%%m.%%d') AS start_label,
            DATE_FORMAT(DATE_ADD(week_start, INTERVAL 6 DAY), '%%m.%%d') AS end_label,
            (income - spend) AS net
        FROM agg
        ORDER BY week_start
        """

        cur.execute(sql, (n_weeks, user_id))
        rows = cur.fetchall()

        labels = [f"{r['start_label']}~{r['end_label']}" for r in rows]
        net    = [int(r['net'] or 0) for r in rows]
        return {"labels": labels, "net": net}

    finally:
        if cur: cur.close()
        if db: db.close()


def select_weekly_spend(user_id: int, end_date: date, n_weeks: int = 10):
    db = None
    cur = None
    try:
        db = db_connector()
        cur = db.cursor(pymysql.cursors.DictCursor)

        # 기준 주차 코드
        cur.execute("SELECT YEARWEEK(%s, 6) AS yw_end", (end_date,))
        yw_end = int(cur.fetchone()['yw_end'])

        sql = """
            SELECT
              YEARWEEK(date, 6) AS yw,
              MIN(DATE_SUB(date, INTERVAL WEEKDAY(date) DAY)) AS week_start,
              SUM(
                CASE WHEN type = '출금'
                     THEN CAST(REPLACE(amount, ',', '') AS SIGNED)
                     ELSE 0
                END
              ) AS spend
            FROM ledger
            WHERE user_id = %s
              AND YEARWEEK(date, 6) BETWEEN %s - %s + 1 AND %s
            GROUP BY yw
            ORDER BY yw
        """
        cur.execute(sql, (user_id, yw_end, n_weeks, yw_end))
        rows = cur.fetchall()

        spend_by_yw = { int(r['yw']): int(r['spend'] or 0) for r in rows }
        start_by_yw = { int(r['yw']): r['week_start'] for r in rows }

        labels, totals = [], []
        first_yw = yw_end - (n_weeks - 1)
        for k in range(first_yw, yw_end + 1):
            totals.append(spend_by_yw.get(k, 0))
            wk = start_by_yw.get(k)
            labels.append(
                f"{wk.month}/{str(wk.day).zfill(2)}주" if wk else f"{str(k)[-2:]}주차"
            )

        return {'labels': labels, 'totals': totals}

    finally:
        if cur: cur.close()
        if db: db.close()
