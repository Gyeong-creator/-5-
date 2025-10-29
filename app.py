import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from modules.user import select_user_info, select_ledger_by_user

app = Flask(__name__)

# 세션 사용을 위한 비밀 키
app.secret_key = 'your_secret_key_here' # 로그인 기능을 위해 팀원과 동일한 키로 맞추기

# --- 데이터 파일 관리 함수 ---
DATA_FILE = 'transactions.json'

def read_transactions():
    """JSON 파일에서 거래 내역을 읽어옵니다."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def write_transactions(data):
    """거래 내역을 JSON 파일에 저장합니다."""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 사용자 정보 (로그인 시뮬레이션) ---
LOGGED_IN_USER = "사용자"

# --- 라우팅 (경로 설정) ---
@app.route('/')
def index():
    return render_template('ledger.html', username=LOGGED_IN_USER)

@app.route('/ledger')
def ledger_view():
    return render_template('ledger.html', username=LOGGED_IN_USER)

@app.route('/login')
def login_view():
    return render_template('login.html', username=LOGGED_IN_USER)

@app.route('/statistics')
def statistics_view():
    return render_template('statistics.html', username=LOGGED_IN_USER)

@app.route('/transactions')
def get_transactions():
    """
    (조회) DB에서 모든 거래 내역을 JSON으로 반환합니다.
    (기존 JSON 파일 읽기에서 DB 읽기로 변경)
    """
    # 1. (필수) 세션에서 현재 로그인한 사용자 ID 가져오기
    user_id = session.get('user_id')
    if not user_id:
        # 로그인이 안 되어 있으면 빈 데이터를 반환 (JS 오류 방지)
        return jsonify({'transactions': []}) 

    # 2. DB에서 데이터 조회
    transactions_list = select_ledger_by_user(user_id)
    
    # 3. 날짜 객체를 JS가 읽을 수 있는 문자열로 변환
    for item in transactions_list:
        if 'date' in item and hasattr(item['date'], 'isoformat'):
            item['date'] = item['date'].isoformat()
            
    # 4. JS가 기대하는 {'transactions': [...]} 형태로 반환
    return jsonify({'transactions': transactions_list})

@app.route('/add', methods=['POST'])
def add_transaction():
    """새로운 거래 내역을 추가하고 전체 내역을 반환합니다."""
    if request.is_json:
        new_transaction = request.get_json()
        transactions = read_transactions()
        transactions.append(new_transaction)
        transactions.sort(key=lambda x: x['date'])
        write_transactions(transactions)
        return jsonify({'transactions': transactions})
    return jsonify({"error": "Request must be JSON"}), 400

@app.route('/delete', methods=['POST'])
def delete_transaction():
    """요청받은 거래 내역과 일치하는 항목을 찾아 삭제합니다."""
    transaction_to_delete = request.get_json()
    transactions = read_transactions()

    # 삭제할 내역과 일치하지 않는 내역만 남겨 새로운 리스트를 생성
    updated_transactions = [t for t in transactions if t != transaction_to_delete]

    write_transactions(updated_transactions)
    # 최신 전체 내역을 다시 반환
    return jsonify({'transactions': updated_transactions})

@app.route('/test')
def test():
    result = select_user_info('yubin', 'yubb')
    return str(result)   

# --- 서버 실행 ---
if __name__ == "__main__":
    app.run(debug=True, port=8080)