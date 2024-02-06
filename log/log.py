from models.meta import SingletonMeta
from datetime import datetime
import os

class Log(metaclass=SingletonMeta):
    def __init__(self, transactions_log_path="./transactions.log", actions_log_path="./cinema.log"):
        # checks if the instance is already initialized
        if not hasattr(self, 'initialized'): 
            self.transactions_log_path = transactions_log_path
            self.actions_log_path = actions_log_path
            # checks log directories exist
            os.makedirs(os.path.dirname(transactions_log_path), exist_ok=True)
            os.makedirs(os.path.dirname(actions_log_path), exist_ok=True)
            self.initialized = True

    @staticmethod
    def log_transaction(self, message):
        self._write_log(message, self.transactions_log_path)
    
    @staticmethod
    def log_action(self, message):
        self._write_log(message, self.actions_log_path)

    def _write_log(self, message, file_path):
        with open(file_path, "a") as log_file:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"[{timestamp}] {message}\n")
