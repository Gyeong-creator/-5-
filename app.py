from flask import Flask, render_template
app = Flask(__name__)


@app.route('/login')
def login_view():
    return render_template('login.html')

@app.route('/ledger')
def ledger_view():
    return render_template('ledger.html')

@app.route('/statistics')
def statistics_view():
    return render_template('statistics.html')

    

if __name__ == "__main__":
    app.run(debug=False, port=8080)