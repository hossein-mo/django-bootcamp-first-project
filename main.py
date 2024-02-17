
from pathlib import Path
import sys
from controllers.server import TCPServer
from models.initialize import Initialize
from utils.utils import config_loader
from utils.exceptions import DatabaseError

if __name__ == "__main__":
    root_path = Path(__file__).parent
    config_path = root_path.joinpath('config.ini')
    config = config_loader(config_path)
    try:
        log = Initialize.run_log_module(**config['logs'])
        db = Initialize.run_db_connection(config['database'])
        Initialize.create_tables(db)
        Initialize.create_subs()
        cache = Initialize.run_cache_thread()
    except DatabaseError as err:
        print(f"Problem starting server check your logs.")
    else:
        server = TCPServer(**config['server'])
        try:
            server.start_server()
        except KeyboardInterrupt:
            print('Stopping cache thread ...')
            cache.stop()
            print('Cache thread stopped.')
            log.log_info('Cache thread stopped by user action.')
            print('Stopping server ...')
            server.stop_server()
            print("Server stopped.")
            log.log_info('Server stopped by user request.')
            sys.exit(0)