import os
import sys
from mysql.connector import Error as dbError
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.utils import hash_password
from models.models import User, UserRole
from models.model_exceptions import DuplicatedEntry
from exceptions import UserNotExist, WrongCredentials
from typing import Union, Dict


class UserManagement:
    @staticmethod
    def user_login(username: str, password: str) -> User:
        password = hash_password(password)
        user = User.fetch_obj(where=f'{User.username} = "{username}"')
        if not user:
            print("user doesn't exist")
            raise UserNotExist
        else:
            user = user[0]
            if user.password != password:
                print("wrong password")
                raise WrongCredentials
            user.last_login = datetime.now()
            user.update({User.last_login: user.last_login})
            return user

    @staticmethod
    def create_user(
        username: str,
        password: str,
        email: str,
        phone_number: str,
        role: Union[str, UserRole],
        birth_date: Dict[str, int],
    ) -> User:
        birth_date = date(birth_date["year"], birth_date["month"], birth_date["year"])
        rightnow = datetime.now()
        user = User.create_new(
            username,
            password,
            email,
            phone_number,
            role,
            birth_date,
            rightnow,
            rightnow,
        )
        try:
            user.insert()
        except DuplicatedEntry as err:
            print("entered username or email is taken")
            raise WrongCredentials
