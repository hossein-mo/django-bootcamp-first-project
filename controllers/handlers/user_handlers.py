import os
import sys
import re
from datetime import date
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.handlers.abstract_handler import AbstractHandler
from utils.exceptions import PasswordPolicyNotPassed, InvalidUserInfo, DuplicatedEntry, WrongCredentials
from models.models import User, UserRole
from utils.utils import hash_password


class UsernameVerification(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        username = data["username"]
        if (
            len(username) > 100
            or not re.search(r"[A-Z]", username)
            or not re.search(r"[a-z]", username)
            or not re.search(r"\d", username)
        ):
            raise InvalidUserInfo("Please enter a username with the correct format!")
        return super().handle(data)


class EmailVerification(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not bool(email_pattern.match(data["email"])):
            raise InvalidUserInfo(
                message="Please enter an email with the correct format!"
            )
        return super().handle(data)


class PhoneVerification(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        if 'phone_number' not in data:
            data['phone_number'] = None
        elif data['phone_number']:
            phone_pattern = re.compile(r"^(09[0-3][0-9]-?[0-9]{3}-?[0-9]{4})$")
            if not bool(phone_pattern.match(data["phone_number"])):
                raise InvalidUserInfo(
                    message="Please enter a phone number with the correct format!"
                )
        return super().handle(data)


class BirthDateVerification(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        birth_date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
        if not bool(birth_date_pattern.match(data["birth_date"])):
            raise InvalidUserInfo(
                message="Please enter your birth date in the correct format!"
            )
        year, month, day = [int(x) for x in data["birth_date"].split("-")]
        data["birth_date"] = date(year=year, month=month, day=day)
        return super().handle(data)


class PasswordPolicyVerification(AbstractHandler):
    def __init__(self) -> None:
        self.min_length = 8
        self.include_special = True
        self.include_upper = True
        self.include_lower = True
        self.include_digit = True

        super().__init__()

    def handle(self, data: dict):
        password = data["password"]
        special_char_count = len(re.findall(r"[#@\$&]", password))
        if special_char_count < 2:
            raise PasswordPolicyNotPassed
        if not re.search(r"[A-Z]", password):
            raise PasswordPolicyNotPassed
        if not re.search(r"[a-z]", password):
            raise PasswordPolicyNotPassed
        if not re.search(r"\d", password):
            raise PasswordPolicyNotPassed
        return super().handle(data)


class CreateUserHandler(AbstractHandler):
    def handle(self, data: dict) -> dict:
        user = User.create_new(**data)
        data["user"] = user
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class ChangePassword(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        password = data["password"]
        old_password = data["old_password"]
        user = data["user"]
        if hash_password(old_password) == user.password:
            user.update({User.password: hash_password(password)})
        else:
            raise WrongCredentials('Wrong password!')
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class ProfileInfoUpdate(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        new_username = data["username"]
        new_email = data["email"]
        new_phone_number = data["phone_number"]
        user = data["user"]
        user.update(
            {
                User.username: new_username,
                User.email: new_email,
                User.phone_number: new_phone_number,
            }
        )
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class LoginHandler(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        user = User.authenticate(data)
        user.update_last_login()
        data["user"] = user
        if self._next_handler:
            return super().handle(data)
        else:
            return data


class ChangeUserRole(AbstractHandler):
    def handle(self, data: dict) -> dict | None:
        if data['new_role'] in UserRole:
            if "username" in data:
                username = data["username"]
                affected_user = User.fetch_obj(where=f'{User.username}="{username}"')
            elif "email" in data:
                email = data["email"]
                affected_user = User.fetch_obj(where=f'{User.email}="{email}"')
            if affected_user:
                affected_user = affected_user[0]
                affected_user.role = UserRole(data['new_role'])
                affected_user.update({User.role: affected_user.role})
                data['affected'] = affected_user
            else:
                raise InvalidUserInfo('User not found')
            if self._next_handler:
                return super().handle(data)
            else:
                return data
        else:
            raise InvalidUserInfo("Requested role doesn't exist.")
