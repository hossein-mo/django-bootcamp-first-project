import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from controllers.systems import UserManagement

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
