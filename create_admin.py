import argparse
import os
import sys
from pathlib import Path

from models.initialize import initialize
from utils.utils import config_loader
from utils.exceptions import DatabaseError
from controllers.systems import UserManagement

if __name__ == "__main__":
    root_path = Path(__file__).parent
    config_path = root_path.joinpath('config.ini')
    config = config_loader(config_path)
    try:
        log = initialize.run_log_module(**config['logs'])
        db = initialize.run_db_connection(config['database'])
    except DatabaseError as err:
        print(f"Problem connecting to database. Check your logs.")
sys.path.append(os.path.dirname(__file__))


parser = argparse.ArgumentParser(
    description="Create an admin user with the specified username, email, password, phone number and birth date",
)
parser.add_argument(
    "username", metavar="username", type=str, nargs=1, help="username of the admin user"
)

parser.add_argument(
    "email", metavar="email", type=str, nargs=1, help="email of the admin user"
)

parser.add_argument(
    "password",
    metavar="password",
    type=str,
    nargs=1,
    help="password of the admin user with requierd format.",
)
parser.add_argument(
    "birth_date",
    metavar="birth_date",
    type=str,
    nargs=1,
    help="birth date of the admin user in Y-m-d format. Example: 1990-01-01",
)
parser.add_argument(
    "--phone_number",
    type=str,
    nargs="?",
    help="phone number of the admin user. Example: 09123456789",
)
args = parser.parse_args()
userdata = {}
for argname in args.__dict__:
    if args.__dict__[argname]:
        userdata[argname] = args.__dict__[argname][0]
response, _ = UserManagement.create_admin(userdata)
if response["status"]:
    userinfo = response["data"]
    for line in userinfo:
        print(f"{line} = {userinfo[line]}")
else:
    print(userdata)
    print("Admin user creation failed!")
    print(response["message"])
