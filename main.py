
import sys
from pathlib import Path
from configparser import ConfigParser 

sys.path.append(Path(__file__).parent)
from controllers.server import TCPServer
from models.base_models import Backend

def config_loader(config_path: str) -> dict:
    config = ConfigParser()
    config.read(config_path)
    conf_dict = {}
    for section in config.sections():
        conf_dict[section] = {}
        for option in config.options(section):
            if option == 'pool_size' or option == 'port':
                conf_dict[section][option] = config.getint(section, option)
            else:
                conf_dict[section][option] = config.get(section, option)
    return conf_dict

if __name__ == "__main__":
    root_path = Path(__file__).parent
    config_path = root_path.joinpath('config.ini')
    config = config_loader(config_path)
    Backend.run_db_connection(config['database'])
    server = TCPServer(**config['server'])
    server.start_server()