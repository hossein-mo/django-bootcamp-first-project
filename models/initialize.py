import inspect
import importlib.util
import models.models as mod
from pathlib import Path
from models.base_models import BaseModel
from models.database import DatabaseConnection
from mysql.connector import Error as dbError
from log.log import Log


class initialize:
    @staticmethod
    def run_db_connection(dbconf: dict) -> DatabaseConnection:
        db = DatabaseConnection(**dbconf)
        BaseModel.db_obj = db
        return db

    @staticmethod
    def run_log_module() -> Log:
        log = Log()
        BaseModel.log_obj = log
        return log

    @staticmethod
    def create_tables(db: DatabaseConnection) -> None:
        create_list = [
            mod.User,
            mod.BankAccount,
            mod.Theater,
            mod.Movie,
            mod.Subscription,
            mod.Showtime,
            mod.UserSubscription,
            mod.Comment,
            mod.Order,
            mod.MovieRate,
            mod.TheaterRate,
        ]
        queries = []
        for cls in create_list:
            queries.append(cls.create_table_query())
        db.transaction(queries)
