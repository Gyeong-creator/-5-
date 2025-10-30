import os
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# user.py는 user_db라는 별명으로
import modules.user as user_db 
# ledger.py는 ledger_db라는 별명으로
import modules.ledger as ledger_db 
# --- ▲▲▲ 수정 완료 ▲▲▲ ---

app = Flask(__name__)

# 세션 사용을 위한 비밀 키
app.secret_key = 'your_secret_key_here'

# --- 라우팅 (경로 설정) ---
@app.route('/')
def index():
    return redirect(url_for('login_view'))

@app.route('/ledger')
def ledger_view():
    username = session.get('username', '사용자') 
    return render_template('ledger.html', username=username)

@app.route('/login')
def login_view():
    username = session.get('username', '사용자') 
    return render_template('login.html', username=username)

@app.route('/statistics')
def statistics_view():
    username = session.get('username', '사용자') 
    return render_template('statistics.html', username=username)

@app.route('/transactions')
def get_transactions():
    """ (조회) DB에서 모든 거래 내역을 JSON으로 반환합니다. """
    user_id = session.get('user_id')
    if not user_id:
        session['user_id'] = 1 # 테스트용 임시 로그인
        user_id = 1
        # (나중에 로그인 기능이 완성되면 이 2줄을 지우세요)

    transactions_list = ledger_db.select_ledger_by_user(user_id)
    
    for item in transactions_list:
        if 'date' in item and hasattr(item['date'], 'isoformat'):
            item['date'] = item['date'].isoformat()
            
    return jsonify({'transactions': transactions_list})

@app.route('/add', methods=['POST'])
def add_transaction():
    """ (수정) 새로운 거래 내역을 DB에 추가합니다. """
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    if request.is_json:
        data = request.get_json()
        try:
            ledger_db.insert_transaction(
                user_id,
                data.get('date'),
                data.get('type'),
                data.get('desc'),
                data.get('amount'),
                category=None 
            )
            
            latest_transactions = ledger_db.select_ledger_by_user(user_id)
            for item in latest_transactions:
                if 'date' in item and hasattr(item['date'], 'isoformat'):
                    item['date'] = item['date'].isoformat()

            return jsonify({'transactions': latest_transactions})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    return jsonify({"error": "Request must be JSON"}), 400

@app.route('/delete', methods=['POST'])
def delete_transaction():
    """ (수정) 요청받은 ID의 거래 내역을 DB에서 삭제합니다. """
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    if request.is_json:
        data = request.get_json()
        transaction_id = data.get('id')
        
        try:
            ledger_db.delete_transaction_by_id(transaction_id, user_id)
            
            latest_transactions = ledger_db.select_ledger_by_user(user_id)
            for item in latest_transactions:
                if 'date' in item and hasattr(item['date'], 'isoformat'):
                    item['date'] = item['date'].isoformat()
            
            return jsonify({'transactions': latest_transactions})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 400

@app.route('/test')
def test():
    result = user_db.select_user_info('yubin', 'yubb')
    return jsonify(result)   

# --- 서버 실행 ---
if __name__ == "__main__":
    app.run(debug=True, port=8080)