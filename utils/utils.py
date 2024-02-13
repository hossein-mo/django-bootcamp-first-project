import hashlib
from configparser import ConfigParser 


def hash_password(password: str) -> str:
    """Hash the input string with sha256 algorithm

    Args:
        password (str): input string

    Returns:
        str: hashed input in string format
    """

    password_bytes = password.encode("utf-8")
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    hashed_password = sha256_hash.hexdigest()

    return hashed_password


def create_response(status: bool, type: str, message: str, data: dict | list = {}):
    return {"status": status, "type": type, "message": message, "data": data}

def config_loader(config_path: str) -> dict:
    """loads configs from config.ini

    Args:
        config_path (str): config file path

    Returns:
        dict: dictionary of configs
    """    
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