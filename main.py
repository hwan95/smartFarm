from database import UserDatabase

# 데이터베이스 연결 정보
host = '172.16.10.57'
user = 'test'
password = 'test'
database = 'mydb'

# UserDatabase 객체 생성
db = UserDatabase(host, user, password, database)

# 새로운 사용자 추가
user_id = '12345S'
user_name = 'John'
password = 'password1234'
db.add_user(user_id, user_name, password)


#site 정보 추가
site_id = '01'
db.add_site(user_id, site_id)

#기상청 데이터 받아오기
from WeatherDB import Weather
service_key = "Q8bq6Cu0SbunyPYsVSE5cMj3YcUciY0kFrfm0ltvzQjCu7KbRCmp/t+yP0mHR6XeQ9BIBAH4Il5Bc1si+wiqmA=="
site_id = '01'

weather = Weather(db_host='localhost', db_user='root', db_password='1234', db_name='mydb', service_key= service_key, nx = 98, ny = 73, site_id = site_id)
weather_data = weather.get_weather_data()
