import mysql.connector

class DatabaseConnection:
    _instance = None
    host='localhost'
    user ='root'
    password =''
    db_name = 'pytonilia_db'

    # def __new__(cls, *args, **kwargs):
    #     if not cls._instance:
    #         cls._instance = super(DatabaseConnection, cls).__new__(cls, *args, **kwargs)
    #         cls._instance.connection = mysql.connector.connect(
    #             host= cls.host,
    #             user= cls.user,
    #             password= cls.password,
    #             database=cls.db_name
    #         )
    #     return cls._instance
    
    @classmethod
    def get_connection(cls):
        """Create a database if not exist and return the connection."""
        try:
            connection = mysql.connector.connect(
                host= DatabaseConnection.host,
                user=DatabaseConnection.user,
                password=DatabaseConnection.password,
                database=DatabaseConnection.db_name
            )
            return connection

        except mysql.connector.Error as e:
            if e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                # Database does not exist, create it
                connection = mysql.connector.connect(
                    host=DatabaseConnection.host,
                    user=DatabaseConnection.user,
                    password=DatabaseConnection.password
                )

                cursor = connection.cursor()
                cursor.execute(f'CREATE DATABASE {DatabaseConnection.db_name} COLLATE utf8_persian_ci')
                from models.user import User
                User.create_table()
                from models.bank_account import BankAccount
                BankAccount.create_table()
                from models.movie import Movie
                Movie.create_table()
                # from models.comment import Comment
                # Comment.create_table()
                from models.subscription import Subscription
                Subscription.create_table()
                # from models.user_subscription import UserSubscription
                # UserSubscription.create_table()
                cursor.close()

                connection = mysql.connector.connect(
                    host=DatabaseConnection.host,
                    user=DatabaseConnection.user,
                    password=DatabaseConnection.password,
                    database=DatabaseConnection.db_name
                )

                return connection

            else:
                print("Error while connecting to MySQL", e)