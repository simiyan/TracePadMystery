import sqlite3
import uuid
from flask import Flask, request, redirect, jsonify, make_response, render_template

app = Flask(__name__)
DATABASE = 'data.db'


def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(
        'CREATE TABLE IF NOT EXISTS tokens (token TEXT PRIMARY KEY, username TEXT)'
    )
    conn.commit()
    conn.close()


@app.before_first_request
def setup_db():
    init_db()


def get_username(token: str) -> str | None:
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('SELECT username FROM tokens WHERE token = ?', (token,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None


@app.route('/')
def index():
    token = request.cookies.get('token')
    if token and get_username(token):
        return redirect('/mypage')
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    if not username:
        return jsonify({'error': 'username required'}), 400
    token = uuid.uuid4().hex
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('INSERT INTO tokens (token, username) VALUES (?, ?)', (token, username))
    conn.commit()
    conn.close()
    resp = make_response(jsonify({'token': token}))
    resp.set_cookie('token', token, httponly=True)
    return resp


@app.route('/mypage')
def mypage():
    token = request.cookies.get('token')
    username = get_username(token) if token else None
    if not username:
        return redirect('/')
    return render_template('mypage.html', username=username)


@app.route('/logout', methods=['POST'])
def logout():
    token = request.cookies.get('token')
    if token:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('DELETE FROM tokens WHERE token = ?', (token,))
        conn.commit()
        conn.close()
    resp = make_response(jsonify({'status': 'logged out'}))
    resp.delete_cookie('token')
    return resp


if __name__ == '__main__':
    app.run(debug=True)
