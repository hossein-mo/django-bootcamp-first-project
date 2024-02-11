import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import controllers.handlers.user_handlers as uHandlers
import controllers.handlers.account_handlers as baHandlers
import controllers.handlers.cinema_handlers as cHandlers
import utils.exceptions as Excs
import models.models as mod
from loging.log import Log
from models.base_models import UserRole
from controllers.authorization import authorize
from utils.utils import create_response


class UserManagement:
    loging: Log

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
    def authenticate(request: dict) -> mod.User | None:
        data = request["data"]
        if request["type"] == "login":
            user = UserManagement.login(data)
        elif request["type"] == "signup":
            user = UserManagement.sign_up(data)
        else:
            raise Excs.AuthenticationFaild
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
        except Excs.WrongCredentials:
            response = create_response(
                False, "user", "Wrong credential, please try again!"
            )
        except Excs.InvalidUserInfo as err:
            response = create_response(False, "user", err.message)
        except Excs.PasswordPolicyNotPassed:
            response = create_response(False, "user", err.message)
        except Excs.DuplicatedEntry as err:
            response = create_response(False, "user", "Username or email are in use!")
        except Excs.AuthenticationFaild as err:
            response = create_response(
                False, "user", "User authentication faild. Please login."
            )
        return response, user

    @staticmethod
    def edit_profile(user: mod.User, data: dict):
        data["user"] = user
        username = user.username
        useremail = user.email
        userphone = user.phone_number
        handler = uHandlers.UsernameVerification()
        email = uHandlers.EmailVerification()
        phone_number = uHandlers.PhoneVerification()
        profile_update = uHandlers.ProfileInfoUpdate()
        handler.set_next(email).set_next(phone_number).set_next(profile_update)
        try:
            handler.handle(data)
            response = create_response(True, "user", "Profile updated.", user.info())
            UserManagement.loging.log_action(
                f"User changed its user info. username: {username} -> {user.username}"
                + f"email: {useremail} -> {user.email}, {userphone} -> {user.phone_number}"
            )
        except Excs.InvalidUserInfo as err:
            response = create_response(False, "user", err.message)
        except Excs.DuplicatedEntry as err:
            response = create_response(False, "user", "Username or email are in use!")
        finally:
            return response, user

    @staticmethod
    def change_password(user: mod.User, data: dict):
        handler = uHandlers.PasswordPolicyVerification()
        change_password = uHandlers.ChangePassword()
        handler.set_next(change_password)
        data["user"] = user
        try:
            handler.handle(data)
            response = create_response(
                True, "user", "Password succecfully changed!", user.info()
            )
            UserManagement.loging.log_action(
                f"User with username {user.username} changed its password"
            )
        except Excs.PasswordPolicyNotPassed as err:
            response = create_response(False, "user", err.message)
        except Excs.WrongCredentials as err:
            UserManagement.loging.log_action(
                f"Wrong credentials for changing password. username: {user.username}."
            )
            response = create_response(False, "user", err.message)
        finally:
            return response

    @staticmethod
    def create_admin(userdata: dict) -> tuple:
        request = {"type": "signup", "data": userdata}
        return UserManagement.client_authenticatation(request, role=UserRole.ADMIN)

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN})
    def change_user_role(user: mod.User, data: dict):
        change_role = uHandlers.ChangeUserRole()
        try:
            data = change_role.handle(data)
            res_message = f"User role succesfully changed!"
            res_status = True
            affected = data["affected"]
            UserManagement.loging.log_action(
                f"user with username {affected.username} role changed to {affected.role} "
                + f"by admin with username {user.username} and id {user.id}"
            )
        except Excs.InvalidUserInfo as err:
            res_message = err.message
            res_status = False
        response = create_response(res_status, "user", res_message)
        return response


class AccountManagement:
    loging: Log

    @staticmethod
    def add_account_user(user: mod.User, data: dict) -> dict:
        data = {"user": user, "card_info": data}
        account = baHandlers.AddAccount()
        try:
            data = account.handle(data)
            AccountManagement.loging.log_action(
                f"New bank account added for user. username: {user.username}, id: {user.id}"
            )
            return create_response(
                True,
                "account",
                "Bank account has been added to your profile.",
                data["card_info"],
            )
        except Excs.InvalidRequest as err:
            return create_response(False, "account", err.message)

    @staticmethod
    def get_user_accounts(user) -> List[mod.BankAccount]:
        user_accs = mod.BankAccount.fetch_obj(
            where=f"{mod.BankAccount.user_id} = {user.id}"
        )
        return create_response(
            True, "account", "", data={"accounts": [acc.info() for acc in user_accs]}
        )

    # @staticmethod
    # def money_transfer(user: User, request: dict) -> dict:
    #     data = request['data']
    #     data['user'] = user
    #     data['amount'] = int(data['amount'])
    #     if request['subtype'] == 'deposit':
    #         data['origin'] = 'deposit'
    #         if data['dest'] == 'userbalance':
    #             data['dest'] = user
    #         else:
    #             data['dest'] = int(data['dest'])
    #     elif request['subtype'] == 'withdrawal':
    #         data['dest'] == 'withdrawal'
    #         data['origin'] = int(data['origin'])
    #     elif request['subtype'] == 'transfer':

    # @staticmethod
    # def wallet_deposit(user: User, account_id: int) -> None:
    #     account = BankAccount.fetch_obj(
    #         where=f'{BankAccount.id} = "{account_id}" AND {BankAccount.user_id} = "{user.id}"'
    #     )


class CinemaManagement:
    loging: Log

    @staticmethod
    def process(user: mod.User, request: dict):
        data = request["data"]
        if request["subtype"] == "addmovie":
            response = CinemaManagement.add_movie(user, data)
        if request["subtype"] == "addtheater":
            response = CinemaManagement.add_theater(user, data)
        if request["subtype"] == "addshow":
            response = CinemaManagement.add_show(user, data)
        else:
            raise KeyError
        return response

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN, UserRole.STAFF})
    def add_movie(user: mod.User, data: dict) -> dict:
        handler = cHandlers.CheckMovieInfo()
        add_movie = cHandlers.AddMovie()
        handler.set_next(add_movie)
        data = handler.handle(data)
        response = create_response(
            True, "management", "Movie added to the cinema archive.", data=data
        )
        CinemaManagement.loging.log_action(
            f"Movie add to the archive by {user.username}, user id: {user.id}. "
            + f"movie name: {data['m_name']} movie id: {data['id']}"
        )
        return response

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN})
    def add_theater(user: mod.User, data: dict) -> dict:
        handler = cHandlers.CheckTheaterInfo()
        add_theater = cHandlers.AddTheater()
        handler.set_next(add_theater)
        data = handler.handle(data)
        response = create_response(
            True, "management", "Theater added to the cinema.", data=data
        )
        CinemaManagement.loging.log_action(
            f"Theater add to the cinema by {user.username}, user id: {user.id}. "
            + f"theater name: {data['t_name']} theater id: {data['id']}"
        )
        return response

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN, UserRole.STAFF})
    def add_show(user: mod.User, data: dict):
        handler = cHandlers.CheckTheater()
        movie_check = cHandlers.CheckMovie()
        time_check = cHandlers.CheckShowTime()
        add_show = cHandlers.AddShow()
        try:
            handler.set_next(movie_check).set_next(time_check).set_next(add_show)
            data = handler.handle(data)
            status = True
            message = "Show has benn added!"
            data = data["show"]
            CinemaManagement.loging.log_action(
                f"Show add to the cinema by {user.username}, user id: {user.id}. "
                + f"theater id: {data['theater_id']} movie id: {data['movie_id']}"
                + f" start date: {data['start_date']}, end date: {data['end_date']}"
            )
        except (Excs.TheaterNotExist, Excs.MovieNotExist, Excs.ShowTimeError) as err:
            status = False
            message = err.message
            data = {}

        return create_response(status, "management", message, data)


class Reports:
    # loging: Log

    @staticmethod
    def process(user: mod.User, request: dict):
        data = request["data"]
        if request["subtype"] == "theaterlist":
            response = Reports.get_theaters(user)
        if request["subtype"] == "movielist":
            response = Reports.get_movies(user)
        else:
            raise Excs.InvalidRequest
        return response

    @staticmethod
    @authorize(authorized_roles={UserRole.ADMIN, UserRole.STAFF})
    def get_theaters(user: mod.User):
        data = mod.Theater.get_theater_list()
        response = create_response(True, "report", "List of theaters!", data=data)
        return response

    @staticmethod
    def get_movies(user: mod.User):
        data = mod.Movie.get_movies_list()
        response = create_response(True, "report", "List of movies!", data=data)
        return response
