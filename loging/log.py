from models.meta import SingletonMeta
from datetime import datetime
import os
import threading
from pathlib import Path

class Log(metaclass=SingletonMeta):
    def __init__(
        self,
        location = 'default',
    ):
        """log writing module

        Args:
            location (str, optional): root location of the log folder by default it is PROJECT_ROOT/logs, can be change in config.ini. Defaults to 'default'.
        """        
        # checks if the instance is already initialized
        if location == 'default':
            logs_root = Path(__file__).parent.parent.joinpath('logs')
        else:
            logs_root = Path(location)
        os.makedirs(logs_root, exist_ok=True)
        self.transactions_log_path = logs_root.joinpath("transactions.log")
        self.actions_log_path = logs_root.joinpath("cinema.log")
        self.errors_log_path = logs_root.joinpath("errors.log")
        self.info_log_path = logs_root.joinpath("info.log")
        # Create locks for each log file
        self.transactions_log_lock = threading.Lock()
        self.actions_log_lock = threading.Lock()
        self.errors_log_lock = threading.Lock()
        self.info_log_lock = threading.Lock()
        # checks log directories exist

    def log_info(self, message: str) -> None:
        """write log to the info file, this are server info like connection and disconnection of clients.

        Args:
            message (str): log message
        """
        with self.info_log_lock:
            self._write_log(message, self.info_log_path)

    def log_errors(self, message: str) -> None:
        """write error logs.
        Args:
            message (str): log message
        """
        with self.errors_log_lock:
            self._write_log(message, self.errors_log_path)

    def log_transaction(self, message: str) -> None:
        """write transactions logs.

        Args:
            message (str): log message
        """
        with self.transactions_log_lock:
            self._write_log(message, self.transactions_log_path)

    def log_action(self, message: str) -> None:
        """write action logs like adding movies.

        Args:
            message (str): log message
        """
        with self.actions_log_lock:
            self._write_log(message, self.actions_log_path)

    def _write_log(self, message:  str, file_path: str) -> None:
        """log writing function to files

        Args:
            message (str): log message
            file_path (str): log file path
        """        
        with open(file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
