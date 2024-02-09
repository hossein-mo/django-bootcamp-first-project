
import sys
from pathlib import Path
from configparser import ConfigParser 

sys.path.append(Path(__file__).parent)
from controllers.server import TCPServer
from models.database import DatabaseConnection



if __name__ == "__main__":
    root_path = Path(__file__).parent
    config_path = root_path.joinpath('config.ini')
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
    db = DatabaseConnection(**conf_dict['database'])
    server = TCPServer(**conf_dict['server'])
    server.start_server()