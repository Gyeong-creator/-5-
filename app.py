import modules.user as user_db
import modules.ledger as ledger_db
import modules.config as config
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from datetime import timedelta
from functools import wraps

# ====================== flask & session & setting values ======================
app = Flask(__name__)
app.secret_key = config.secret  
app.permanent_session_lifetime = timedelta(hours=6)  # session validate time

# security option(HTTPS)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
    # SESSION_COOKIE_SECURE=True
)

DATA_FILE = 'transactions.json'




# ====================== preprocess ======================
# Expose session values (e.g., username, role) globally to all templates
@app.context_processor
def inject_user():
    return {
        'username': session.get('username'),
        'id': session.get('id')
    }


@app.before_request
def require_login_for_all_except_public():
    public_endpoints = {'login_view', 'login', 'static'}  # 로그인 없이 접근 허용
    ep = (request.endpoint or '').split('.')[0]           # blueprint 대비

    if ep in public_endpoints:
        return 

    if not session.get('id'):
        # JSON 요청이면 JSON으로, 그 외는 로그인 페이지로
        if request.is_json or request.path.startswith(('/add', '/delete', '/transactions')):
            return jsonify(success=False, message='Login required'), 401
        return redirect(url_for('login_view', next=request.path))




# ====================== 라우팅 (경로 설정) ======================
@app.route('/')
def index():
    if session.get('id'):
        return redirect(url_for('ledger_view'))
    return render_template('login.html')


@app.route('/login')
def login_view():
    if session.get('id'):
        return redirect(url_for('ledger_view'))
    return render_template('login.html')


@app.route('/ledger')
def ledger_view():
    return render_template('ledger.html')


@app.route('/statistics')
def statistics_view():
    return render_template('statistics.html')



# ====================== ledger ======================
@app.route('/transactions')
def get_transactions():
    user_id = session.get('id')
    transactions_list = ledger_db.select_ledger_by_user(user_id)
    
    print(transactions_list)
    for item in transactions_list:
        if 'date' in item and hasattr(item['date'], 'isoformat'):
            item['date'] = item['date'].isoformat()
            
    return jsonify({'transactions': transactions_list})


@app.route('/add', methods=['POST'])
def add_transaction():
    """ (수정) 새로운 거래 내역을 DB에 추가합니다. """
    
    user_id = session.get('id')
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
    
    user_id = session.get('id')
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

@app.route('/edit', methods=['POST'])
def edit_transaction():
    """ (신규) 요청받은 ID의 거래 내역을 DB에서 수정합니다. """
    
    user_id = session.get('id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    if request.is_json:
        data = request.get_json()
        
        # JS에서 보낼 4가지 새 값 + 1개 ID
        transaction_id = data.get('id')
        new_date = data.get('date')
        new_type = data.get('type')
        new_desc = data.get('desc') # JS에서 'desc'로 보냅니다
        new_amount = data.get('amount')

        if not all([transaction_id, new_date, new_type, new_desc, new_amount is not None]):
             return jsonify({'error': '모든 값이 필요합니다.'}), 400

        try:
            # modules/ledger.py 에 새로 만들 함수
            ledger_db.update_transaction(
                transaction_id, 
                user_id, 
                new_date, 
                new_type, 
                new_desc, 
                new_amount
            )
            
            # JS가 스스로 목록을 새로고침하므로, 성공 메시지만 반환
            return jsonify({'success': True})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({"error": "Request must be JSON"}), 400

# ====================== auth ======================
@app.route('/login_check', methods=['POST'])
def login():
    data = request.get_json()
    id = data.get('id')
    password = data.get('password')

    result = user_db.select_user_info(id, password)
    if result == None:
        return jsonify(success=False)
    
    session['id'] = result['id']       
    session['username'] = result['user_name']   
    session.permanent = True
    
    nxt = request.args.get('next') or data.get('next')

    if not nxt or not nxt.startswith('/'):
        nxt = url_for('index')
    return jsonify(success=True, next=nxt)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear() 
    return redirect(url_for('login_view'))
    


# ====================== server ======================
if __name__ == "__main__":
    app.run(debug=True, port=8080)