import mysql.connector
import os
import sys
from mysql.connector import pooling
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from meta import SingletonMeta


class DatabaseConnection(metaclass=SingletonMeta):
    HOST = "localhost"
    PORT = "3307"
    USER = "root"
    PASSWORD = "pass"
    DB_NAME = "pytonilia_db"
    POOL_SIZE = 5

    def create_db_if_not_exist(self, db_config: dict) -> None:
        with mysql.connector.connect(**db_config) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SHOW DATABASES LIKE "{self.db_name}";')
            database_exists = cursor.fetchone()
            if not database_exists:
                cursor.execute(f"CREATE DATABASE {self.db_name};")
            connection.commit()
            cursor.close()

    def __init__(self, db_name=DB_NAME) -> None:
        self.__dbconfig = {
            "host": self.HOST,
            "port": self.PORT,
            "user": self.USER,
            "password": self.PASSWORD,
        }
        try:
            self.create_db_if_not_exist(self.__dbconfig)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        else:
            self.__dbconfig["database"] = self.db_name
            self.pool = pooling.MySQLConnectionPool(
                pool_size=self.POOL_SIZE, pool_reset_session=True, **self.__dbconfig
            )

    def execute(self, query: str) -> List[int]:
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        connection.commit()
        rowscount = cursor.rowcount
        lastrowid = cursor.lastrowid
        cursor.close()
        connection.close()
        return rowscount, lastrowid

    def fetch(self, query: str) -> list:
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def transaction(self, query_list: List[str]) -> int:
        connection = self.pool.get_connection()
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)
        try:
            for query in query_list:
                cursor.execute(query)
            connection.commit()
        except mysql.connector.Error as err:
            connection.rollback()
            raise
        else:
            rowscount = cursor.rowcount
            return rowscount
        finally:
            cursor.close()
            connection.close()
