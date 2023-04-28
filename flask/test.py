from flask import Flask, render_template, request, session, redirect, url_for
from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['MYSQL_HOST'] = '172.16.10.57'
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'mydb'
mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/farm/v1/login', methods=['POST'])
def login():
    id = request.form['id']
    password = request.form['password']
    cursor = mysql.connection.cursor()
    sql = 'SELECT * FROM users WHERE user_id = %s AND password = %s'
    values = (id, password)
    cursor.execute(sql, values)
    user = cursor.fetchone()

    if user:
        session['id'] = user[0]
        session['name'] = user[2]
        return {'result': 'success', 'user_id': user[0]}
    else:
        return {'result': 'fail', 'message': 'Invalid login credentials'}
    
@app.route('/FARM/v1/change_password', methods=['POST'])
def change_password():
    # 현재 비밀번호, 새 비밀번호, 비밀번호 확인 값 받아오기
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # 새 비밀번호와 비밀번호 확인 값이 같은지 확인
    if new_password != confirm_password:
        return jsonify({'message': 'New password and confirm password do not match.'}), 400
    
    # 현재 사용자의 id 가져오기
    user_id = session.get('id')
    
    # 현재 비밀번호가 맞는지 확인
    cursor = mysql.connection.cursor()
    sql = 'SELECT * FROM mydb.users WHERE user_id = %s AND password = %s'
    values = (user_id, current_password)
    cursor.execute(sql, values)
    user = cursor.fetchone()
    if user is None:
        return jsonify({'message': 'Invalid current password.'}), 400

    # 새 비밀번호로 업데이트하기
    sql = 'UPDATE mydb.users SET password = %s WHERE user_id = %s'
    values = (new_password, user_id)
    cursor.execute(sql, values)
    mysql.connection.commit()
    
    return jsonify({'message': 'Password changed successfully.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
