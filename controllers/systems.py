from cgitb import handler
from lib2to3.fixes.fix_operator import invocation
import os
import sys
from typing import List
from urllib import response

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import controllers.handlers.user_handlers as uHandlers
import controllers.handlers.account_handlers as baHandlers
import controllers.handlers.cinema_handlers as cHandlers
import controllers.handlers.review_handlers as rHandlers
import controllers.handlers.order_handlers as oHandlers
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
    def process(user: mod.User, request: dict):
        if request["subtype"] == "info":
            response = create_response(True, "user", "", data=user.info())
        elif request["subtype"] == "update":
            response = UserManagement.edit_profile(user, request["data"])
        elif request["subtype"] == "changepass":
            response = UserManagement.change_password(user, request["data"])
        elif request["subtype"] == "changerole":
            response = UserManagement.change_user_role(user, request["data"])
        return response

    @staticmethod
    def edit_profile(user: mod.User, data: dict):
        data["user"] = user
        if "username" not in data:
            data["username"] = user.username
        if "email" not in data:
            data["email"] = user.email
        if "phone_number" not in data:
            data["phone_number"] = user.phone_number
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
        return response

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
    def process(user: mod.User, request: dict):
        data = request["data"]
        if request["subtype"] == "add":
            response = AccountManagement.add_account_user(user, data)
        elif request["subtype"] == "list":
            response = AccountManagement.get_user_accounts(user)
        elif request["subtype"] == "deposit":
            data["dest"] = user.accounts[int(data["account_id"])]
            data["card"] = data["dest"]
            data["origin"] = "deposit"
            data["transfer_type"] = "deposit"
            response = AccountManagement.account_transfer(user, data)
        elif request["subtype"] == "withdraw":
            data["origin"] = user.accounts[int(data["account_id"])]
            data["card"] = data["origin"]
            data["password"] = str(data["password"])
            data["cvv2"] = str(data["cvv2"])
            data["dest"] = "withdraw"
            data["transfer_type"] = "withdraw"
            response = AccountManagement.account_transfer(user, data)
        elif request["subtype"] in {"transfer", "userbalance"}:
            if request["subtype"] == "transfer":
                data["origin"] = user.accounts[int(data["from_id"])]
                data["dest"] = user.accounts[int(data["to_id"])]
                data["transfer_type"] = request["subtype"]
            else:
                data["origin"] = user.accounts[int(data["account_id"])]
                data["dest"] = user
                data["transfer_type"] = request["subtype"]
            data["password"] = str(data["password"])
            data["cvv2"] = str(data["cvv2"])
            response = AccountManagement.account_transfer(user, data)
        else:
            raise KeyError
        return response

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
        return create_response(
            True, "account", "", data=[acc.info() for acc in user.accounts.values()]
        )

    @staticmethod
    def account_transfer(user: mod.User, data: dict) -> None:
        handler = baHandlers.AccountCredentialsCheck()
        balance_check = baHandlers.BalanceCheck()
        transf = baHandlers.TransferHandler()
        try:
            handler.set_next(balance_check).set_next(transf)
            if data["transfer_type"] == "transfer":
                log_message = (
                    f"User {data['transfer_type']}, amount: {data['amount']} from card number: "
                    + f"{data['origin'].card_number}, card id: {data['dest'].id}. to card number: "
                    + f"{data['dest'].card_number}, card id: {data['dest'].id}. "
                    + f"username: {user.username}, user id: {user.id}"
                )
                res_message = (
                    f"Your {data['transfer_type']} of {data['amount']} from {data['origin'].card_number} "
                    + f"to {data['dest'].card_number} was successful"
                )
            elif data["transfer_type"] == "userbalance":
                log_message = (
                    f"User adds fund to wallet, amount: {data['amount']} from card number: "
                    + f"{data['origin'].card_number}, card id: {data['dest'].id}. "
                    + f"username: {user.username}, user id: {user.id}, user balance: {user.balance} ."
                )
                res_message = f"{data['amount']} added to your balance."
            else:
                log_message = (
                    f"User {data['transfer_type']}, amount: {data['amount']} card number: "
                    + f"{data['card'].card_number}, card id: {data['card'].id}. "
                    + f"username: {user.username}, user id: {user.id}"
                )
                res_message = f"Your {data['transfer_type']} of {data['amount']} was successful. Affected card number {data['card'].card_number} "
            data = handler.handle(data)
            status = True
        except (Excs.WrongBankAccCreds, Excs.NotEnoughBalance) as err:
            log_message = (
                f"Failed transfer of money reason: {err.message}, info: " + log_message
            )
            res_message = err.message
            status = False
        AccountManagement.loging.log_transaction(log_message)
        return create_response(
            status,
            "account",
            message=res_message,
        )


class CinemaManagement:
    loging: Log

    @staticmethod
    def process(user: mod.User, request: dict):
        data = request["data"]
        if request["subtype"] == "addmovie":
            response = CinemaManagement.add_movie(user, data)
        elif request["subtype"] == "addtheater":
            response = CinemaManagement.add_theater(user, data)
        elif request["subtype"] == "addshow":
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
        elif request["subtype"] == "movielist":
            response = Reports.get_movies(user)
        elif request["subtype"] == "showlist":
            response = Reports.get_shows(user)
        elif request["subtype"] == "getcomments":
            response = Reports.get_commetns(user, data)
        elif request["subtype"] == "showseats":
            response = Reports.get_seats(user, data)
        elif request["subtype"] == "getsubs":
            response = Reports.get_subs(user)
        elif request["subtype"] == "getorders":
            response = Reports.get_user_orders(user)
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

    @staticmethod
    def get_shows(user: mod.User):
        data = mod.Showtime.get_shows_list()
        response = create_response(True, "report", "List of shows!", data=data)
        return response

    @staticmethod
    def get_commetns(user: mod.User, data: dict):
        comms = mod.Comment.get_comments(data["movie_id"])
        response = create_response(
            True, "report", "List of shows!", data={"commetns": comms}
        )
        return response

    @staticmethod
    def get_seats(user: mod.User, data: dict):
        data["show_id"] = int(data["show_id"])
        seats = mod.Showtime.get_reserved_seat(data["show_id"])
        response = create_response(
            True,
            "report",
            "List of reserved seats!",
            data={"show_id": data["show_id"], "reserved_seats": seats},
        )
        return response

    @staticmethod
    def get_subs(user: mod.User):
        subs = mod.Subscription.fetch()
        response = create_response(True, "report", "List of reserved seats!", data=subs)
        return response

    @staticmethod
    def get_user_orders(user: mod.User):
        data = mod.Order.get_user_orders(user)
        response = create_response(True, "report", "List of user orders!", data=data)
        return response


class Review:
    loging: Log

    @staticmethod
    def process(user: mod.User, request: dict):
        if "data" in request:
            data = request["data"]
        if request["subtype"] == "movierate":
            response = Review.submmit_movie_rate(user, data)
        elif request["subtype"] == "theaterrate":
            response = Review.submmit_theater_rate(user, data)
        elif request["subtype"] == "comment":
            response = Review.write_comment(user, data)
        else:
            raise Excs.InvalidRequest
        return response

    @staticmethod
    def submmit_movie_rate(user: mod.User, data: dict):
        data["user"] = user
        handler = rHandlers.SubmitMovieRate()
        try:
            handler.handle(data)
            Review.loging.log_action(
                f"Review submited. username: {user.username}, "
                + f"user id {user.id}, movie id: {data['movie_id']}, rate: {data['rate']}"
            )
        except Excs.UnvalidRate as err:
            return create_response(False, "review", err.message)
        return create_response(True, "review", "Movie rate submited.")

    def submmit_theater_rate(user: mod.User, data: dict):
        data["user"] = user
        handler = rHandlers.SubmitTheaterRate()
        try:
            handler.handle(data)
            Review.loging.log_action(
                f"Review submited. username: {user.username}, "
                + f"user id {user.id}, theater id: {data['theater_id']}, rate: {data['rate']}"
            )
        except Excs.UnvalidRate as err:
            return create_response(False, "review", err.message)
        return create_response(True, "review", "Theater review submited.")

    def write_comment(user: mod.User, data: dict):
        data["user"] = user
        handler = rHandlers.WriteComment()
        handler.handle(data)
        comm = data["comment"]
        Review.loging.log_action(f"User wrote a comment. info: {comm.info()}")
        return create_response(True, "review", "", comm.info())


class OrderManagement:
    loging: Log

    @staticmethod
    def process(user: mod.User, request: dict) -> dict:
        if "data" in request:
            data = request["data"]
        if request["subtype"] == "subs":
            response = OrderManagement.order_subs(user, data)
        elif request["subtype"] == "pre_invoice":
            response = OrderManagement.ticket_pre_invoice(user, data)
        elif request["subtype"] == "reserve":
            response = OrderManagement.reserve_seat(user, data)
        elif request["subtype"] == "cancel":
            response = OrderManagement.cancel_reservation(user, data)
        else:
            raise Excs.InvalidRequest
        return response

    @staticmethod
    def order_subs(user: mod.User, data: dict) -> dict:
        data["dest"] = "withdraw"
        data["origin"] = user
        data["user"] = user
        handler = oHandlers.SubCheck()
        balance_check = baHandlers.BalanceCheck()
        transf = baHandlers.TransferHandler()
        buy_sub = oHandlers.BuySub()
        inovice = oHandlers.CreateSubInovice()
        handler.set_next(balance_check).set_next(transf).set_next(buy_sub).set_next(
            inovice
        )
        try:
            data = handler.handle(data)
            response = create_response(
                True, "order", "Order successful!", data=data["inovice"]
            )
            OrderManagement.loging.log_transaction(
                f"User bought a {user.subs.s_name} subscription, username: {user.name}"
            )
        except (Excs.NotFound, Excs.NotEnoughBalance) as err:
            response = create_response(False, "order", err.message)
        return response

    def ticket_pre_invoice(user: mod.User, data: dict) -> dict:
        data["user"] = user
        handler = oHandlers.CalculateDiscountedPrice()
        try:
            data = handler.handle(data)
        except Excs.NotFound as err:
            response = create_response(False, "invoice", err.message)
        response = create_response(True, "invoice", "", data=data["pre_invoice"])
        return response

    def reserve_seat(user: mod.User, data: dict) -> dict:
        data["user"] = user
        data["dest"] = "withdraw"
        data["origin"] = user
        handler = oHandlers.CalculateDiscountedPrice()
        seat_check = oHandlers.SeatCheck()
        balance_check = baHandlers.BalanceCheck()
        transf = baHandlers.TransferHandler()
        reserve = oHandlers.ReserveSeat()
        invoice = oHandlers.CreateOrderInovice()
        handler.set_next(seat_check).set_next(balance_check).set_next(transf).set_next(
            reserve
        ).set_next(invoice)
        try:
            data = handler.handle(data)
            order = data["order"]
            response = create_response(
                True, "order", "Order successful!", data=data["inovice"]
            )
            OrderManagement.loging.log_transaction(
                f"User reserved seat number {order.seat_number} for show id {order.showtime_id}, username: {user.name}"
            )
        except (Excs.NotFound, Excs.NotEnoughBalance) as err:
            response = create_response(False, "order", err.message)

        return response

    def cancel_reservation(user: mod.User, data: dict) -> dict:
        data["user"] = user
        handler = oHandlers.CalculateCancelationFine()
        cancel = oHandlers.CancelOrder()
        invoice = oHandlers.CancelInvoice()
        handler.set_next(cancel).set_next(invoice)
        try:
            data = handler.handle(data)
            response = create_response(
                True, "order", "Order canceld!", data=data["inovice"]
            )
            OrderManagement.loging.log_transaction(
                f"User canceld reservation, user id: {user.id} username: {user.name}. "
                + f'Cancellation info: {data["inovice"]}'
            )
        except Excs.NotFound as err:
            response = create_response(False, "order", err.message)
        return response
