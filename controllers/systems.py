import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import controllers.handlers.user_handlers as uHandlers
import controllers.exceptions as cExcept
import models.model_exceptions as mExcept
from models.models import User
from models.base_models import UserRole
from controllers.autorization import authorize
from utils.utils import create_response


class UserManagement:
    @staticmethod
    def get_safe_user_info(user: User) -> dict:
        return {
            "username": user.username,
            "email": user.email,
            "phone_number": user.phone_number,
            "birth_date": user.birth_date,
            "last_login": user.last_login,
            "register_date": user.register_date,
            "wallet": user.wallet,
            "role": user.role.value,
        }

    @staticmethod
    def login(data: dict):
        login_handler = uHandlers.LoginHandler()
        user = login_handler.handle(data)
        return user

    @staticmethod
    def sign_up(data: dict, role: UserRole):
        data["role"] = role
        signup_handler = uHandlers.UsernameVerification()
        email = uHandlers.EmailVerification()
        phome_number = uHandlers.PhoneVerification()
        birth_date = uHandlers.BirthDateVerification()
        password_policy = uHandlers.PasswordPolicyVerification()
        create_user = uHandlers.CreateUserHandler()
        signup_handler.set_next(email).set_next(phome_number).set_next(
            birth_date
        ).set_next(password_policy).set_next(create_user)
        user = signup_handler.handle(data)
        return user


    @staticmethod
    def authenticate(request: dict, role: UserRole = UserRole.USER):
        data = request["data"]
        print(request)
        if request["type"] == "login":
            user = UserManagement.login(data)
        elif request["type"] == "signup":
            user = UserManagement.sign_up(data, role)
        else:
            raise cExcept.AuthenticationFaild
        return user

    @staticmethod
    def client_authenticatation(request):
        user = None
        try:
            user = UserManagement.authenticate(request)
            user_info = UserManagement.get_safe_user_info(user)
            response = create_response(
                True, "user", "Authentication succesfull.", user_info
            )
        except mExcept.WrongCredentials:
            print("Invalid Credentials")
            response = create_response(
                False, "user", "Wrong credential, please try again!", {}
            )
        except cExcept.InvalidUserInfo as err:
            print(err)
            response = create_response(False, "user", "Invalid user info!", {})
        except cExcept.PasswordPolicyNotPassed as err:
            print(err)
            response = create_response(False, "user", "Invalid password!", {})
        except mExcept.DuplicatedEntry as err:
            print(err)
            response = create_response(
                False, "user", "Username or email are in use!", {}
            )
        except cExcept.AuthenticationFaild as err:
            print(err)
            response = create_response(
                False, "user", "User authentication faild. Please login.", {}
            )
        finally:
            return response, user

    @staticmethod
    def edit_profile(data: dict, user: User):
        handler = uHandlers.UsernameVerification()
        email = uHandlers.EmailVerification()
        phone_number = uHandlers.PhoneVerification()
        profile_update = uHandlers.ProfileInfoUpdate()
        handler.set_next(email).set_next(phone_number).set_next(profile_update)
        try:
            handler.handle(data)
            user_info = UserManagement.get_safe_user_info(user)
            response = create_response(
                True, "user", "Authentication succesfull.", user_info
            )
        except cExcept.InvalidUserInfo as err:
            print(err)
            response = create_response(False, "user", "Invalid user info!", {})
        except mExcept.DuplicatedEntry as err:
            print(err)
            response = create_response(
                False, "user", "Username or email are in use!", {}
            )
        finally:
            return response, user

    @staticmethod
    def change_password(data: dict, user: User):
        handler = uHandlers.PasswordPolicyVerification()
        change_password = uHandlers.ChangePassword()
        handler.set_next(change_password)
        try:
            handler.handle(data)
            user_info = UserManagement.get_safe_user_info(user)
            response = create_response(
                True, "user", "Authentication succesfull.", user_info
            )
        except cExcept.PasswordPolicyNotPassed as err:
            print(err)
            response = create_response(False, "user", "Invalid password!", {})
        finally:
            return response, user

    @staticmethod
    def create_admin(userdata: dict):
        return UserManagement.sign_up(userdata, role=UserRole.ADMIN)
    
    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN})
    def change_user_role (user: User, user_to_change_role: dict, new_role: str):
        pass