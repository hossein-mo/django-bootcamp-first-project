import models.models as mod
import controllers.systems as systms
from models.base_models import BaseModel
from models.database import DatabaseConnection
from controllers.server import TCPServer
from loging.log import Log


class initialize:
    @staticmethod
    def run_db_connection(dbconf: dict) -> DatabaseConnection:
        db = DatabaseConnection(**dbconf)
        BaseModel.db_obj = db
        return db

    @staticmethod
    def run_log_module(location: str = "default") -> Log:
        log = Log(location=location)
        DatabaseConnection.loging = log
        BaseModel.loging = log
        TCPServer.loging = log
        systms.UserManagement.loging = log
        systms.AccountManagement.loging = log
        systms.ArchiveManagement.loging = log

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
