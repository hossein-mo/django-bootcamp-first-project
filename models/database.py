import mysql.connector
import os
import sys
from mysql.connector import pooling
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.meta import SingletonMeta


class DatabaseConnection(metaclass=SingletonMeta):
    HOST = "localhost"
    PORT = "3307"
    USER = "root"
    PASSWORD = "123456"
    DB_NAME = "pytonilia_db"
    POOL_SIZE = 5

    def create_db_if_not_exist(self, db_config: dict) -> None:
        """Create database if it doesn't exist.

        Args:
            db_config (dict): database configuration
        """
        with mysql.connector.connect(**db_config) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SHOW DATABASES LIKE "{self.DB_NAME}";')
            database_exists = cursor.fetchone()
            if not database_exists:
                cursor.execute(f"CREATE DATABASE {self.DB_NAME};")
            connection.commit()
            cursor.close()

    def __init__(
        self,
        host: str = HOST,
        port: str = PORT,
        user: str = USER,
        password: str = PASSWORD,
        db_name: str = DB_NAME,
        pool_size: int = POOL_SIZE,
    ) -> None:
        """Constructor for DatabaseConnection class

        Args:
            db_name (str, optional): database name. Defaults to DB_NAME.
        """
        self.HOST = host
        self.PORT = port
        self.USER = user
        self.PASSWORD = password
        self.DB_NAME = db_name
        self.POOL_SIZE = pool_size
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
            self.__dbconfig["database"] = self.DB_NAME
            self.pool = pooling.MySQLConnectionPool(
                pool_size=self.POOL_SIZE, pool_reset_session=True, **self.__dbconfig
            )

    def execute(self, query: str) -> Tuple[int]:
        """Execute query on database. Use for NSERT and UPDATE queries.

        Args:
            query (str): query in string format

        Returns:
            Tuple[int]: A tuple with number of affected rows as first element \
            and id of the last row inserted on table as second element 
        """
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        connection.commit()
        rowscount = cursor.rowcount
        lastrowid = cursor.lastrowid
        cursor.close()
        connection.close()
        return (rowscount, lastrowid)

    def fetch(self, query: str) -> list:
        """Executes query on database and returns a list of dictionaries where each one representing a row in table. \
        Use for SELECT queries.

        Args:
            query (str): query in string format

        Returns:
            list: List of dictionaries
        """
        connection = self.pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result

    def transaction(self, query_list: List[str]) -> int:
        """Executes list of queries on database. Can be used for INSERT and UPDATE queries.
        Args:
            query_list (List[str]): list of queries

        Returns:
            int: Number of affected rows
        """
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
