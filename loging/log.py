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
        # checks if the instance is already initialized
        if not hasattr(self, "initialized"):
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
            self.initialized = True

    def log_info(self, message):
        # Use the transactions lock
        with self.info_log_lock:
            self._write_log(message, self.info_log_path)

    def log_errors(self, message):
        # Use the transactions lock
        with self.errors_log_lock:
            self._write_log(message, self.errors_log_path)

    def log_transaction(self, message):
        # Use the transactions lock
        with self.transactions_log_lock:
            self._write_log(message, self.transactions_log_path)

    def log_action(self, message):
        # Use the actions lock
        with self.actions_log_lock:
            self._write_log(message, self.actions_log_path)

    def _write_log(self, message, file_path):
        with open(file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
