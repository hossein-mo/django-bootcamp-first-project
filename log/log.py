from models.meta import SingletonMeta
from datetime import datetime
import os
import threading
from pathlib import Path

class Log(metaclass=SingletonMeta):
    def __init__(
        self,
        transactions_log_path: str = "transactions.log",
        actions_log_path: str = "cinema.log",
    ):
        # checks if the instance is already initialized
        if not hasattr(self, "initialized"):
            self.transactions_log_path = Path(__file__).parent.parent.joinpath(transactions_log_path)
            self.actions_log_path = Path(__file__).parent.parent.joinpath(actions_log_path)
            # Create locks for each log file
            self.transactions_log_lock = threading.Lock()
            self.actions_log_lock = threading.Lock()
            # checks log directories exist
            print()
            os.makedirs(Path(__file__).parent.parent, exist_ok=True)
            os.makedirs(Path(__file__).parent.parent, exist_ok=True)
            self.initialized = True

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
