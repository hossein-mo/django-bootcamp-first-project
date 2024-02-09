import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import controllers.handlers.user_handlers as uHandlers
import controllers.handlers.account_handlers as baHandlers
import controllers.exceptions as cExcept
import models.model_exceptions as mExcept
from models.models import User, BankAccount
from models.base_models import UserRole
from controllers.autorization import authorize
from utils.utils import create_response


class UserManagement:

    @staticmethod
    def login(data: dict):
        login_handler = uHandlers.LoginHandler()
        data = login_handler.handle(data)
        user = data["user"]
        return user

    @staticmethod
    def sign_up(data: dict):
        signup_handler = uHandlers.UsernameVerification()
        email = uHandlers.EmailVerification()
        phome_number = uHandlers.PhoneVerification()
        birth_date = uHandlers.BirthDateVerification()
        password_policy = uHandlers.PasswordPolicyVerification()
        create_user = uHandlers.CreateUserHandler()
        signup_handler.set_next(email).set_next(phome_number).set_next(
            birth_date
        ).set_next(password_policy).set_next(create_user)
        data = signup_handler.handle(data)
        user = data["user"]
        return user

    @staticmethod
    def authenticate(request: dict) -> User | None:
        data = request["data"]
        if request["type"] == "login":
            user = UserManagement.login(data)
        elif request["type"] == "signup":
            user = UserManagement.sign_up(data)
        else:
            raise cExcept.AuthenticationFaild
        return user

    @staticmethod
    def client_authenticatation(request, role: UserRole = UserRole.USER):
        user = None
        if request["type"] == "signup":
            request["data"]["role"] = role
        try:
            user = UserManagement.authenticate(request)
            response = create_response(
                True, "user", "Authentication succesfull.", user.info()
            )
        except mExcept.WrongCredentials:
            print("Invalid Credentials")
            response = create_response(
                False, "user", "Wrong credential, please try again!"
            )
        except cExcept.InvalidUserInfo as err:
            print(err)
            response = create_response(False, "user", "Invalid user info!")
        except cExcept.PasswordPolicyNotPassed:
            response = create_response(False, "user", "Invalid password!")
        except mExcept.DuplicatedEntry as err:
            print(err)
            response = create_response(False, "user", "Username or email are in use!")
        except cExcept.AuthenticationFaild as err:
            print(err)
            response = create_response(
                False, "user", "User authentication faild. Please login."
            )
        finally:
            return response, user

    @staticmethod
    def edit_profile(user: User, data: dict):
        data["user"] = user
        handler = uHandlers.UsernameVerification()
        email = uHandlers.EmailVerification()
        phone_number = uHandlers.PhoneVerification()
        profile_update = uHandlers.ProfileInfoUpdate()
        handler.set_next(email).set_next(phone_number).set_next(profile_update)
        try:
            handler.handle(data)
            response = create_response(
                True, "user", "Authentication succesfull.", user.info()
            )
        except cExcept.InvalidUserInfo as err:
            print(err)
            response = create_response(False, "user", "Invalid user info!")
        except mExcept.DuplicatedEntry as err:
            print(err)
            response = create_response(False, "user", "Username or email are in use!")
        finally:
            return response, user

    @staticmethod
    def change_password(user: User, data: dict):
        handler = uHandlers.PasswordPolicyVerification()
        change_password = uHandlers.ChangePassword()
        handler.set_next(change_password)
        data["user"] = user
        try:
            handler.handle(data)
            response = create_response(
                True, "user", "Password succecfully changed!", user.info()
            )
        except cExcept.PasswordPolicyNotPassed as err:
            print(err)
            response = create_response(False, "user", err.message)
        except mExcept.WrongCredentials as err:
            response = create_response(False, "user", err.message)
        finally:
            return response

    @staticmethod
    def create_admin(userdata: dict) -> tuple:
        request = {"type": "signup", "data": userdata}
        return UserManagement.client_authenticatation(request, role=UserRole.ADMIN)

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN})
    def change_user_role(user: User, data: dict):
        change_role = uHandlers.ChangeUserRole()
        try:
            change_role.handle(data)
            res_message = f"User role succesfully changed!"
            res_status = True
        except cExcept.InvalidUserInfo as err:
            print(err)
            res_message = err.message
            res_status = False
        response = create_response(res_status, "user", res_message)
        return response


class AccountManagement:
    @staticmethod
    def add_account_user(user: User, data: dict) -> dict:
        data = {'user': user, 'card_info': data}
        account = baHandlers.AddAccount()
        try:
            data = account.handle(data)
            return create_response(True, 'account', "Bank account has been added to your profile.", data['card_info'])
        except KeyError as err:
            return create_response(False, 'account', "Invalid card info.")
        except TypeError as err:
            return create_response(False, 'account', "Invalid card info.")
        except cExcept.InvalidRequest as err:
            return create_response(False, 'account', err.message)
            

    # @staticmethod
    # def get_user_accounts(user) -> List[BankAccount]:
    #     user_accs = BankAccount.fetch_obj(where=f"{BankAccount.user_id} = {user.id}")
    #     return user_accs

    # @staticmethod
    # def wallet_deposit(user: User, account_id: int) -> None:
    #     account = BankAccount.fetch_obj(
    #         where=f'{BankAccount.id} = "{account_id}" AND {BankAccount.user_id} = "{user.id}"'
    #     )
