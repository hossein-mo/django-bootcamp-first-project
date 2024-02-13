import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils import create_request, Page, clear_screen, Response, CinemaReservationApp
from bankaccounts import AccountListPage
from movie import MovieListPage
from order import UserOrdersPage
from showtime import ShowsPage
from theater import TheaterListPage
from tcp_client import TCPClient

class User:
    def __init__(self, username, email, birth_date, phone_number, subs:str, subs_expires_in, balance, role, last_login, register_date):
        self.username = username
        self.email = email
        self.birth_date = birth_date
        self.phone = phone_number
        self.subscription = subs
        self.subscription_rest_days = subs_expires_in
        self.balance = balance
        self.role = role


class ProfilePage(Page):
    user = None
    def __init__(self, app, user:User):
        super().__init__(app)
        ProfilePage.user = user

    def display(self):
        clear_screen()
        print(f'username: {self.user.username}')
        print(f'email: {self.user.email}')
        print(f'subscription: {self.user.subscription} -> <{self.user.subscription_rest_days}> days left\n')
        print(f'1. edit profile\n2. change password\n3. bank account\n4. orders history')
        print(f'5. shows list\n6. movies list\n7. theater list\n8. logout')
        while True:
            user_input = input('Where do you want to go? ')
            if self.handle_input(user_input):
                break

    def handle_input(self, user_input):
        flag = True
        if user_input == '8':
            self.app.restart()
        elif user_input == '1':
            self.app.navigate_to_page(EditProfilePage(self.app, self.user))
        elif user_input == '2':
            self.app.navigate_to_page(ChangePasswordPage(self.app, self.user))
        elif user_input == '3':
            self.app.navigate_to_page(AccountListPage(self.app))
        elif user_input == '4':
            self.app.navigate_to_page(UserOrdersPage(self.app))
        elif user_input == '5':
            self.app.navigate_to_page(ShowsPage(self.app))
        elif user_input == '6':
            self.app.navigate_to_page(MovieListPage(self.app))
        elif user_input == '7':
            self.app.navigate_to_page(TheaterListPage(self.app))
        else:
            print(f'Invalid input!')
            flag = False
        return flag
        


class EditProfilePage(Page):
    
    def __init__(self, app: CinemaReservationApp, user: User):
        super().__init__(app)
        self.user = user

    def display(self):
        clear_screen()


class ChangePasswordPage(Page):
    
    def __init__(self, app: CinemaReservationApp, user: User):
        super().__init__(app)
        self.user = user

    def display(self):
        clear_screen()