import mysql.connector
import os
import sys
from mysql.connector import pooling
from typing import List, Tuple

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.meta import SingletonMeta
from loging.log import Log
from utils.exceptions import DatabaseError


class DatabaseConnection(metaclass=SingletonMeta):
    loging: Log

    def create_db_if_not_exist(self, db_config: dict) -> None:
        """Create database if it doesn't exist.

        Args:
            db_config (dict): database configuration
        """
        with mysql.connector.connect(**db_config) as connection:
            cursor = connection.cursor()
            cursor.execute(f'SHOW DATABASES LIKE "{self.db_name}";')
            database_exists = cursor.fetchone()
            if not database_exists:
                cursor.execute(f"CREATE DATABASE {self.db_name};")
            connection.commit()
            cursor.close()

    def __init__(
        self,
        host: str = "localhost",
        port: str = "3306",
        user: str = "root",
        password: str = "pass",
        db_name: str = "pytonilia_db",
        pool_size: int = 5,
    ) -> None:
        """Constructor for DatabaseConnection class

        Args:
            db_name (str, optional): database name. Defaults to DB_NAME.
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.pool_size = pool_size
        self.__dbconfig = {
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
        }
        try:
            self.create_db_if_not_exist(self.__dbconfig)
        except mysql.connector.Error as err:
            self.loging.log_errors(err.msg)
            raise DatabaseError
        else:
            self.__dbconfig["database"] = self.db_name
            self.pool = pooling.MySQLConnectionPool(
                pool_size=self.pool_size, pool_reset_session=True, **self.__dbconfig
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
        print(query)
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
            raise DatabaseError
        else:
            rowscount = cursor.rowcount
            return rowscount
        finally:
            cursor.close()
            connection.close()
