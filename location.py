import pymysql

# MySQL connection 정보
host = 'localhost'
user = 'root'
password = '1234'
db = 'mydb'

def get_grid_coordinates(level1, level2, level3):
    # MySQL 연결
    conn = pymysql.connect(host=host, user=user, password=password, db=db, charset='utf8')
    curs = conn.cursor()
    
    # 쿼리 작성 및 실행
    query = f"SELECT `nx`, `ny` FROM location WHERE `addr1`='{level1}' AND `addr2`='{level2}' AND `addr3`='{level3}'"
    curs.execute(query)
    result = curs.fetchone()
    
    # 결과값 처리
    if result:
        grid_x, grid_y = result
        return grid_x, grid_y
    else:
        return None
