import pymysql
import py.config as config   # config.py 전체 불러오기

def db_connector():
    db = pymysql.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.passwd,
        db=config.db,
        charset='utf8mb4'
    )
    print("✅ MySQL 연결 성공")
    return db


def select_user_info(id, pw):
    db = db_connector()
    cursor = db.cursor(pymysql.cursors.DictCursor)  # dict 반환

    try:
        query = "SELECT * FROM user WHERE id = %s AND password = %s"
        cursor.execute(query, (id, pw))

        result = cursor.fetchall()
        if not result:
            return None
        return result
    finally:
        cursor.close()
        db.close()
