import os
import sys
import re
from datetime import date
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from controllers.handlers.abstract_handler import AbstractHandler
from controllers.exceptions import PasswordPolicyNotPassed, InvalidUserInfo
from models.models import User
from models.model_exceptions import DuplicatedEntry, WrongCredentials
from utils.utils import hash_password


class EmailVerification(AbstractHandler):
    def handle(self, data: Any) -> Any | None:
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not bool(email_pattern.match(data["email"])):
            raise InvalidUserInfo(
                message="Please enter an email with the correct format!"
            )
        return super().handle(data)


class PhoneVerification(AbstractHandler):
    def handle(self, data: Any) -> Any | None:
        phone_pattern = re.compile(r"^(09[0-3][0-9]-?[0-9]{3}-?[0-9]{4})$")
        if not bool(phone_pattern.match(data["phone_number"])) and not None:
            raise InvalidUserInfo(
                message="Please enter a phone number with the correct format!"
            )
        return super().handle(data)


class BirthDateVerification(AbstractHandler):
    def handle(self, data: Any) -> Any | None:
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

    def handle(self, data: Dict[str, str]):
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
    def handle(self, data: Any) -> User | None:
        try:
            user = User.create_new(**data)
        except DuplicatedEntry as err:
            raise
        if self._next_handler:
            return super().handle(data)
        else:
            return user


class ChangePassword(AbstractHandler):
    def handle(self, data: Any, user: User) -> User | None:
        password = data["password"]
        old_password = data["old_password"]
        user = data["user_obj"]
        if hash_password(old_password) == user.password:
            user.update({User.password: hash_password(password)})
        if self._next_handler:
            return super().handle(data)
        else:
            return user


class ProfileInfoUpdate(AbstractHandler):
    def handle(self, data: Any, user: User) -> User | None:
        new_username = data["username"]
        new_email = data["email"]
        new_phone_number = data["phone_number"]
        try:
            user.update(
                {
                    User.username: new_username,
                    User.email: new_email,
                    User.phone_number: new_phone_number,
                }
            )
        except DuplicatedEntry as err:
            raise
        if self._next_handler:
            return super().handle(data)
        else:
            return user


class LoginHandler(AbstractHandler):
    def handle(self, data: Any) -> User | None:
        try:
            user = User.autenthicate(data)
        except WrongCredentials as err:
            raise
        else:
            if self._next_handler:
                return super().handle(data)
            else:
                return user
