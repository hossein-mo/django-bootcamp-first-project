import mysql.connector
import os
import sys
from mysql.connector import pooling
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from meta import SingletonMeta


class DatabaseConnection(metaclass=SingletonMeta):
    host = "localhost"
    port = "3306"
    user = "root"
    password = "pass"
    db_name = "pytonilia_db"
    pool_size = 5

    def create_db_if_not_exist(self, db_config: dict) -> None:
        with mysql.connector.connect(**db_config) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SHOW DATABASES LIKE "{self.db_name}";')
            database_exists = cursor.fetchone()
            if not database_exists:
                cursor.execute(f"CREATE DATABASE {self.db_name};")
            connection.commit()
            cursor.close()

    def __init__(self) -> None:
        self.__dbconfig = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
        }
        try:
            self.create_db_if_not_exist(self.__dbconfig)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        else:
            self.__dbconfig["database"] = self.db_name
            self.pool = pooling.MySQLConnectionPool(
                pool_size=self.pool_size, pool_reset_session=True, **self.__dbconfig
            )

    def execute(self, query: str) -> int:
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        connection.commit()
        rowscount = cursor.rowcount
        cursor.close()
        connection.close()
        return rowscount

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
