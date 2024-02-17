# django-bootcamp-first-project

## Requirements
Requirements are avilable in `requirement.txt`. Right now the only external requirement is `mysql-connector-python==8.3.0`. Also it is required to use `python=3.10` but it is advised to use `python=3.11`.

## Server Configuration
Before running the server you have to set your database connection, and also host and the port that server listen to in `config.ini`.
```ini
[server]
host = localhost
port = 8000

[database]
host = localhost
port = 3306
user = root
password = pass
db_name = pytonilia_db
pool_size = 5

[logs]
location = default
```

## Creating Admin User
Using `create_admin.py` you can create admin users. You have to use this script on the server machine to create the first admin user.
```
python create_admin.py -h

usage: create_admin.py [-h] [--phone_number [PHONE_NUMBER]] username email password birth_date

Create an admin user with the specified username, email, password, phone number and birth date

positional arguments:
  username              username of the admin user
  email                 email of the admin user
  password              password of the admin user with requierd format.
  birth_date            birth date of the admin user in Y-m-d format. Example: 1990-01-01

options:
  -h, --help            show this help message and exit
  --phone_number [PHONE_NUMBER]
                        phone number of the admin user. Example: 09123456789
```

## Running The Server
You can run the server by running `main.py`.
```bash
python main.py
```

## Requests
List of accepted requests by the server can be found in the link below:

[Request list](https://docs.google.com/spreadsheets/d/1hEW496VUH2yVqaGEIK5vBeTh-_lR9JziVvb1IQfMKnQ/edit?usp=sharing)

## About this
This is a server and client implementation for a cinema reservation system.
### Design Patterns
[Singleton design pattern](https://refactoring.guru/design-patterns/singleton/python/example) used for Database connection module, Log writing module and TCP Client module.
###
Server Controller uses [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility/python/example) design pattern to handle requests.
