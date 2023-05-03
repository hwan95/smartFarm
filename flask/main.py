from flask import Flask, request
from flask import jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from datetime import timedelta
import RPi.GPIO as GPIO

app = Flask(__name__)
app.secret_key = 'my_secret_key'
app.config['JSON_AS_ASCII'] = False
# app.config['SESSION_TYPE'] = 'filesystem'

app.config['MYSQL_HOST'] = '172.16.10.57'
app.config['MYSQL_USER'] = 'test'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'mydb'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
# Session(app)

####아두이노 

# 팬 작동 함수
def fan_on():
    try:
        GPIO.output(23, GPIO.HIGH) # High 신호 전달
        return "on"
    except expression as identifier:
        return "fail"

# 팬 중지 함수
def fan_off():
    try:
        GPIO.output(23, GPIO.LOW) # Low 신호 전달
        return "off"
    except Exception as identifier:
        return "fail"
    
# 조도 센서 작동
# @app.route("/led/on")
def led_on():
    try:
        GPIO.output(14, GPIO.HIGH)
        return "on"
    except Exception as identifier:
        return "fail"


# @app.route("/led/off")
def led_off():
    try:
        GPIO.output(14, GPIO.LOW)
        return "off"
    except expression as identifier:
        return "fail"
    
@app.route('/FARM/{user_id}/{site_id}/CONTROL/ETC/ETC_2', methods = ['POST']) # 환풍기 전원
def control_fan(user_id, site_id):
    status = request.json.get('status')
    if status == 'on':
        # 팬 작동 코드 추가
        fan_on()
        return '팬 작동 요청 성공', 200
    elif status == 'off':
        # 팬 중지 코드 추가
        fan_off() 
        return '팬 중지 요청 성공', 200  
    else:
        return '잘못된 요청입니다', 400

@app.route('/FARM/{user_id}/{site_id}/CONTROL/ETC/ETC_3', methods = ['POST']) #조도센서 전원
def control_ligh(user_id, site_id):
    status = request.json.get('status')
    if status == 'on':
        # 팬 작동 코드 추가
        led_on()
        return '조도센서 작동 요청 성공', 200
    elif status == 'off':
        # 팬 중지 코드 추가
        led_off() 
        return '조도센서 중지 요청 성공', 200  
    else:
        return '잘못된 요청입니다', 400


#로그인
@app.route('/farm/v1/login', methods=['GET','POST'])
# @app.route('/farm/v1/login', methods=['POST'])
def login():
    try :
        # session['id'] =''
        if request.method == 'GET':            
            id = request.args.get('id')
            password = request.args.get('password')
        elif request.method == 'POST':
            id = request.form.get('id')
            password = request.form.get('password')
            print('id : ',id)
        
        #db
        cursor = mysql.connection.cursor()
        sql = 'SELECT * FROM users WHERE user_id = %s AND password = %s'
        values = (id, password)
        cursor.execute(sql, values)
        user = cursor.fetchone()

        if user:
            
            user_id = user[0]
            # session['id'] = user_id
            user_name = user[1]
            e_mail = user[6]

            return jsonify({'user_id': user_id, 'user_name' : user_name, 'e_mail': e_mail}), 200
        else:
            return jsonify({'result': 'fail', 'message': 'Invalid login credentials'}) ,400
    
    except Exception as e:
        print("Error: ", e)
        return jsonify({'error': str(e)}), 500

#비밀 번호 변경
@app.route('/farm/v1/<string:user_id>/change_password', methods=['GET', 'POST'])
def change_password(user_id):
    try:
        # GET 방식일 경우
        if request.method == 'GET':
            current_password = request.args.get('current_password')
            new_password = request.args.get('new_password')
            confirm_password = request.args.get('confirm_password')
            
        elif request.method == 'POST':
            # 현재 비밀번호, 새 비밀번호, 비밀번호 확인 값 받아오기
            current_password = request.form.get("current_password")
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")
            
        # 새 비밀번호와 비밀번호 확인 값이 같은지 확인
        if new_password != confirm_password:
            return jsonify({'message': 'New password and confirm password do not match.'}), 400
        
        # # 현재 사용자의 id 가져오기
        # user_id = session.get('id')
        # if user_id is None:
        #     print("no id")
        #     return jsonify({'message': 'Authentication failed.'}), 401
        
        user_id = user_id
        # 현재 비밀번호가 맞는지 확인
        cursor = mysql.connection.cursor()
        sql = 'SELECT * FROM mydb.users WHERE user_id = %s AND password = %s'
        values = (user_id, current_password)
        cursor.execute(sql, values)
        user = cursor.fetchone()
        if user is None:
            return jsonify({'message': 'Invalid current password.', 'pwd': current_password}), 400

        # 새 비밀번호로 업데이트하기
        sql = 'UPDATE mydb.users SET password = %s WHERE user_id = %s'
        values = (new_password, user_id)
        cursor.execute(sql, values)
        mysql.connection.commit()
        
        return jsonify({'message': 'Password changed successfully.'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}),500



# user 별 site 데이터
@app.route(f'/FARM/<string:user_id>/sites', methods=['GET'])
def get_site_data(user_id):
    try: 
        cursor = mysql.connection.cursor()
        # sql = f"SELECT * FROM mydb.sites WHERE users_user_id = '{user_id}'"
        sql = f"""SELECT s.site_id, s.users_user_id, u.user_name, u.e_mail 
                FROM mydb.sites s JOIN mydb.users u 
                ON s.users_user_id = u.user_id WHERE s.users_user_id = '{user_id}'"""
        cursor.execute(sql)
        site_data = cursor.fetchall()
        if site_data:
            site_list = [site[0] for site in site_data]
            result = {
                'user_id': user_id,
                'user_name': site_data[0][2],
                'e_mail': site_data[0][3],
                'site_ids': site_list
            }
            return jsonify(result),200
        else:
            return jsonify({'message': 'Site not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 외부 환경 데이터 
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/EXTERNAL_SENSOR')
def external_sensor_all(user_id, site_id):
    try:
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

        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# 외부환경 센서 타입별 그래프
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/EXTERNAL_SENSOR/<string:sensor_type>/GRAPH')
def external_sensor_type(user_id, site_id, sensor_type):
    try :
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

        return jsonify(result),200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 내부 환경 데이터 
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/INTERNAL_SENSOR')
def internal_sensor_all(user_id, site_id):
    try:
        cursor = mysql.connection.cursor()
        now = datetime.now()
        date = now.strftime("%Y%m%d")  # 현재 날짜
        time = now.strftime('%H%M')[:-1] + '0' # 10분단위
        # 현재 시간 이전의 데이터 중 가장 최신 값을 가져오기
        sql = "SELECT * FROM mydb.internal WHERE sites_site_id= %s AND in_date <= %s AND in_time <= %s ORDER BY in_date DESC, in_time DESC LIMIT 1"
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

        return jsonify(result) ,200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 내부환경 센서 타입별 그래프
@app.route('/FARM/<string:user_id>/<string:site_id>/MONITORING/INTERNAL_SENSOR/<string:sensor_type>/GRAPH')
def internal_sensor_type(user_id, site_id, sensor_type):
    try:
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

        return jsonify(result) ,200 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods = ['POST'])
def test():
    # cursor = mysql.connection.cursor()
    # user_id = session['id']
    # sql = f"select * from sites where users_user_id = '{user_id}' " 
    # cursor.execute(sql)
    # data = cursor.fetchone()

    # return jsonify(data) 
    # val = request.get_json() 
    val = request.get.form
    return jsonify(result = val)

if __name__ == '__main__':
    app.run( debug = True)
