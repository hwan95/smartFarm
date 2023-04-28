import requests
import json
import pymysql
from datetime import datetime
import pandas as pd
import sys


class Weather:
    
    def __init__(self, service_key, nx, ny, db_host, db_user, db_password, db_name, site_id):
        self.url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        self.service_key = service_key
        self.nx = nx
        self.ny = ny
        self.db_host = db_host
        self.db_user = db_user
        self.db_password = db_password
        self.db_name = db_name
        self.site_id = site_id
        
    def get_weather_data(self):
        now = datetime.now() # 현재 시각 데이터 생성
        base_date = now.strftime('%Y%m%d') # 현재 날짜 YYMMDD 형식

        params = {
            'serviceKey': self.service_key,
            'numOfRows': '1000',
            'pageNo': '1',
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': '0200', #기준시간 임의 설정
            'nx': self.nx,
            'ny': self.ny
        }

        res = requests.get(url=self.url , params=params)
        if res.ok:
            data = res.json()
        else:
            print(f"Error: 기상청 데이터 수신 오류")
            sys.exit(1)

        data = data['response']['body']['items']['item']
        temp = [] # 기온
        hum = [] # 습도
        sky = [] # 하늘 상태
        pty = [] # 강수 유형
        wind_dir = [] #풍향
        wind_speed = [] #풍속
        time = [] #시간
        fcst_date = [] #날짜 
        for i in data :
            if i['category'] == 'TMP': #기온 단위 섭씨
                temp.append(float(i['fcstValue']))
                time.append(i['fcstTime']) #해당 시간
                fcst_date.append(i['fcstDate']) # 해당 날짜  
            elif i['category'] == 'REH': #습도 단위 %
                hum.append(float(i['fcstValue']))
            elif i['category'] =='SKY': # 하늘상태 코드 값 별도 참조
                sky.append(float(i['fcstValue']))
            elif i['category'] =='PTY': # 강수형태 코드값 별도 참조
                pty.append(float(i['fcstValue']))
            elif i['category'] == 'VEC' : # 풍향 단위 deg
                wind_dir.append(float(i['fcstValue']))
            elif i['category'] == 'WSD' : #풍속 단위 m/s
                wind_speed.append(float(i['fcstValue']))


        min_len = min(len(temp), len(hum), len(sky), len(wind_speed), len(wind_dir), len(pty))

        if min_len == 0 : 
            print("no data")
        else:    
            
            db = pymysql.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                db=self.db_name,
                charset='utf8')
            
            curs = db.cursor()

            sql = "INSERT IGNORE INTO external (sites_site_id, ex_date, ex_time, temperature, humidity, sky, wind_speed, wind_dir, rain) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

            for i in range(min_len):
                values = (self.site_id, fcst_date[i], time[i], float(temp[i]), float(hum[i]), float(sky[i]), float(wind_speed[i]), float(wind_dir[i]), float(pty[i]))
                curs.execute(sql, values)

            db.commit()
            db.close()

       
