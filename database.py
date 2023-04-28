import mysql.connector
from pymysql import IntegrityError, Error

class UserDatabase:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def add_user(self, user_id, username, password):
        sql = "INSERT INTO users (user_id, user_name, password) VALUES (%s, %s, %s)"
        val = (user_id, username, password)
        try:
            self.cursor.execute(sql, val)
            self.connection.commit()
            print("가입 완료되었습니다.!")

        except mysql.connector.IntegrityError as e:
            if e.errno == 1062:
                print("Warning: 해당 id {} 는 이미 존재합니다..".format(user_id))
            else:
                print("Error: ", e.msg)

    def add_site(self, user_id, site_id):
        try:
            sql = "INSERT INTO sites (users_user_id, site_id) VALUES (%s, %s)"
            values = (user_id, site_id)
            self.cursor.execute(sql, values)
            site_id = self.cursor.lastrowid
            self.connection.commit()
            print("Done")
            return site_id
        except mysql.connector.Error as error:
            print("에러 발생 {}".format(error))
            

    def __del__(self):
        self.cursor.close()
        self.connection.close()


