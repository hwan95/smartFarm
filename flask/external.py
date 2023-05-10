import requests
import json
from datetime import datetime
import pandas as pd
import sys


def weather():
        service_key = "Q8bq6Cu0SbunyPYsVSE5cMj3YcUciY0kFrfm0ltvzQjCu7KbRCmp/t+yP0mHR6XeQ9BIBAH4Il5Bc1si+wiqmA=="
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst" # 기상청api 동네 단기예보

        now = datetime.now() # 현재 시각 데이터 생성
        base_date = now.strftime('%Y%m%d') # 현재 날짜 YYMMDD 형식
        params = {
            'serviceKey': service_key,
            'numOfRows': '1000',
            'pageNo': '1',
            'dataType': 'JSON',
            'base_date': base_date,
            'base_time': '0200', #기준시간 임의 설정
            'nx': 93,
            'ny': 73
        }

        res = requests.get(url=url , params=params)
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
        for i in data:
            if i['category'] == 'TMP': #기온 단위 섭씨
                temp.append(float(i['fcstValue']))
                time.append(i['fcstTime']) #해당 시간
                fcst_date.append(i['fcstDate']) # 해당 날짜  
            elif i['category'] == 'REH': #습도 단위 %
                hum.append(float(i['fcstValue']))
            elif i['category'] =='PTY': # 강수형태 코드값 별도 참조
                pty_code = int(i['fcstValue'])
                if pty_code == 0:
                    pty.append('맑음')
                elif pty_code == 1:
                    pty.append('비')
                elif pty_code == 2:
                    pty.append('비/눈')
                elif pty_code == 3:
                    pty.append('눈')
                elif pty_code == 4:
                    pty.append('소나기')
            elif i['category'] == 'VEC' : # 풍향 단위 deg
                wind_directions = ['북향', '북동향', '동향', '남동향', '남향', '남서향', '서향', '북서향']
                fcstValue = float(i['fcstValue'])
                direction_idx = int((fcstValue + 22.5 * 0.5) / 22.5) // 8  # 8방위로 나누어서 인덱스 계산
                wind_direction = wind_directions[direction_idx]  # 해당 인덱스에 해당하는 방향 한글 가져오기
                wind_dir.append(wind_direction)
            elif i['category'] == 'WSD' : #풍속 단위 m/s
                wind_speed.append(float(i['fcstValue']))

        return(fcst_date, time , temp, hum, wind_speed, wind_dir, pty)

        # min_len = min(len(temp), len(hum), len(wind_speed), len(wind_dir), len(pty))


