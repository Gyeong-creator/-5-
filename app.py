import os
import json
import modules.user as user
import modules.config as config
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import timedelta


app = Flask(__name__)
app.secret_key = config.secret  
app.permanent_session_lifetime = timedelta(hours=6)  # session validate time

# security option(HTTPS)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    # SESSION_COOKIE_SECURE=True
)

# Expose session values (e.g., username, role) globally to all templates
@app.context_processor
def inject_user():
    return {
        'username': session.get('username')
    }

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
    return render_template('ledger.html')

@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/statistics')
def statistics_view():
    return render_template('statistics.html')

@app.route('/transactions')
def get_transactions():
    """모든 거래 내역을 JSON으로 반환합니다."""
    transactions = read_transactions()
    return jsonify({'transactions': transactions})

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

@app.route('/login_check', methods=['POST'])
def login():
    data = request.get_json()
    id = data.get('id')
    password = data.get('password')

    result = user.select_user_info(id, password)
    if result == None:
        return jsonify(success=False)
    else:
        session['id'] = result['id']       
        session['username'] = result['user_name']   
        session.permanent = True
        return jsonify(success=True)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear() 
    return redirect(url_for('login_view'))
    
# --- 서버 실행 ---
if __name__ == "__main__":
    app.run(debug=True, port=8080)