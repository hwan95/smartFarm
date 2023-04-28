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

# 로그인 화면
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

#비밀 번호 변경
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

# user 별 site 데이터
@app.route(f'/FARM/<user_id>/sites')
def get_site_data(user_id):
    cursor = mysql.connection.cursor()
    sql = f"SELECT * FROM mydb.sites WHERE users_user_id = '{user_id}'"
    cursor.execute(sql)
    site_data = cursor.fetchall()
    if site_data:
        site_list = [{'site_id': site[0], 'user_id': site[1]} for site in site_data]
        # return jsonify(site_list)
        return(site_list)
    else:
        return jsonify({'message': 'Site not found'}), 404

# 외부 환경 데이터 
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/EXTERNAL_SENSOR')
def external_sensor_all(user_id, site_id):
    cursor = mysql.connection.cursor()
    now = datetime.now()
    date = now.strftime("%Y%m%d")  # 현재 날짜
    time = now.strftime("%H00")  # 현재 시간
    sql = f"SELECT * FROM mydb.external WHERE sites_site_id= %s AND ex_date = %s AND ex_time = %s "
    values = (site_id, date, time)
    cursor.execute(sql, values)
    data = cursor.fetchall()
    
    # 컬럼명 리스트 가져오기
    columns = [col[0] for col in cursor.description]
    
    # 컬럼명과 데이터 합치기
    result = []
    for row in data:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[columns[i]] = value
        result.append(row_dict)

    return jsonify(result)


# 외부환경 센서 타입별 그래프
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/EXTERNAL_SENSOR/<string:sensor_type>/GRAPH')
def external_sensor_type(user_id, site_id, sensor_type):
    cursor = mysql.connection.cursor()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_today = today.strftime("%Y%m%d")  # 오늘 날짜
    date_yesterday = yesterday.strftime("%Y%m%d")  # 어제 날짜
    sql = f"""SELECT ex_date, ex_time, {sensor_type} FROM mydb.external 
            WHERE sites_site_id = %s AND ex_date >= %s AND ex_date <= %s"""
    values = (site_id, date_yesterday, date_today)
    cursor.execute(sql, values)
    data = cursor.fetchall()

    # 컬럼명 리스트 가져오기
    columns = [col[0] for col in cursor.description]
    
    # 컬럼명과 데이터 합치기
    result = []
    for row in data:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[columns[i]] = value
        result.append(row_dict)

    return jsonify(result)

# 내부 환경 데이터 
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/INTERNAL_SENSOR')
def internal_sensor_all(user_id, site_id):
    cursor = mysql.connection.cursor()
    now = datetime.now()
    date = now.strftime("%Y%m%d")  # 현재 날짜
    time = now.strftime('%H%M')[:-1] + '0' # 10분단위
    sql = "SELECT * FROM mydb.internal WHERE sites_site_id= %s AND in_date = %s AND in_time = %s "
    values = (site_id, date, time)
    cursor.execute(sql, values)
    data = cursor.fetchall()
    # 컬럼명 리스트 가져오기
    columns = [col[0] for col in cursor.description]
    
    # 컬럼명과 데이터 합치기
    result = []
    for row in data:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[columns[i]] = value
        result.append(row_dict)

    return jsonify(result)

# 내부환경 센서 타입별 그래프
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/INTERNAL_SENSOR/<string:sensor_type>/GRAPH')
def internal_sensor_type(user_id, site_id, sensor_type):
    cursor = mysql.connection.cursor()
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    date_today = today.strftime("%Y%m%d")  # 오늘 날짜
    date_yesterday = yesterday.strftime("%Y%m%d")  # 어제 날짜
    sql = f"""SELECT  in_date, in_time, {sensor_type} FROM mydb.internal 
            WHERE sites_site_id = %s AND in_date >= %s AND in_date <= %s"""
    values = (site_id, date_yesterday, date_today)
    cursor.execute(sql, values)
    data = cursor.fetchall()
    # 컬럼명 리스트 가져오기
    columns = [col[0] for col in cursor.description]
    
    # 컬럼명과 데이터 합치기
    result = []
    for row in data:
        row_dict = {}
        row_dict['in_date'] = row[0]
        row_dict['in_time'] = row[1]
        row_dict[sensor_type] = row[2]
        result.append(row_dict)

    return jsonify(result)

@app.route('/test')
def test():
    cursor = mysql.connection.cursor()
    sql = "select * from external where sites_site_id = '02' " 
    cursor.execute(sql)
    data = cursor.fetchone()

    return jsonify(data) 

if __name__ == '__main__':
    app.run( debug = True)
