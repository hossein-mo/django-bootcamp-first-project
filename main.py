
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent)
from controllers.server import TCPServer
from models.initialize import initialize
from utils.utils import config_loader
from utils.exceptions import DatabaseError

if __name__ == "__main__":
    root_path = Path(__file__).parent
    config_path = root_path.joinpath('config.ini')
    config = config_loader(config_path)
    try:
        log = initialize.run_log_module(**config['logs'])
        db = initialize.run_db_connection(config['database'])
        initialize.create_tables(db)
    except DatabaseError as err:
        print(f"Problem starting server check your logs.")
    else:
        server = TCPServer(**config['server'])
        server.start_server()